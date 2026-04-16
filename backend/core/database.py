"""
Database connection and query utilities for AlloyDB.

Supports two connection modes:
  - Local dev: raw asyncpg with host/port (ALLOYDB_USE_CONNECTOR=false)
  - Production: AlloyDB Connector with IAM auth (ALLOYDB_USE_CONNECTOR=true)
"""
import asyncpg
import structlog
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager
from .config import settings

logger = structlog.get_logger()


class Database:
    """AlloyDB connection manager with dual-mode support."""
    
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
        self._connector = None  # AlloyDB AsyncConnector instance
    
    async def connect(self):
        """Create connection pool to AlloyDB."""
        if self.pool is not None:
            return
        
        if settings.alloydb_use_connector:
            await self._connect_with_connector()
        else:
            await self._connect_direct()
    
    async def _connect_direct(self):
        """Connect using raw asyncpg (local development)."""
        logger.info(
            "Connecting to database (direct mode)",
            host=settings.alloydb_host,
            database=settings.alloydb_database,
        )
        self.pool = await asyncpg.create_pool(
            host=settings.alloydb_host,
            port=settings.alloydb_port,
            database=settings.alloydb_database,
            user=settings.alloydb_user,
            password=settings.alloydb_password,
            min_size=5,
            max_size=20,
            command_timeout=60
        )
        logger.info("Database connected (direct mode)")
    
    async def _connect_with_connector(self):
        """Connect using AlloyDB Connector (production)."""
        try:
        from google.cloud.alloydb.connector import Connector
        
        logger.info(
            "Connecting to database (AlloyDB Connector mode)",
            instance_uri=settings.alloydb_instance_uri,
            iam_auth=settings.alloydb_iam_auth,
        )
        
        self._connector = Connector()
        
        async def getconn():
            conn = await self._connector.connect_async(
                settings.alloydb_instance_uri,
                "asyncpg",
                user=settings.alloydb_user,
                password=settings.alloydb_password if not settings.alloydb_iam_auth else None,
                db=settings.alloydb_database,
                enable_iam_auth=settings.alloydb_iam_auth,
            )
            return conn
        
        self.pool = await asyncpg.create_pool(
            min_size=5,
            max_size=20,
            command_timeout=60,
            connect=getconn,
        )
        logger.info("Database connected (AlloyDB Connector mode)")
    
    async def disconnect(self):
        """Close connection pool and connector."""
        if self.pool:
            await self.pool.close()
            self.pool = None
            logger.info("Database pool closed")
        
        if self._connector:
            await self._connector.close_async()
            self._connector = None
            logger.info("AlloyDB Connector closed")
    
    @asynccontextmanager
    async def acquire(self):
        """Acquire a connection from the pool."""
        if self.pool is None:
            await self.connect()
        
        async with self.pool.acquire() as connection:
            yield connection
    
    async def fetch(self, query: str, *args) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return all rows."""
        async with self.acquire() as conn:
            rows = await conn.fetch(query, *args)
            return [dict(row) for row in rows]
    
    async def fetchrow(self, query: str, *args) -> Optional[Dict[str, Any]]:
        """Execute a SELECT query and return one row."""
        async with self.acquire() as conn:
            row = await conn.fetchrow(query, *args)
            return dict(row) if row else None
    
    async def fetchval(self, query: str, *args) -> Any:
        """Execute a SELECT query and return a single value."""
        async with self.acquire() as conn:
            return await conn.fetchval(query, *args)
    
    async def execute(self, query: str, *args) -> str:
        """Execute an INSERT/UPDATE/DELETE query."""
        async with self.acquire() as conn:
            return await conn.execute(query, *args)
    
    async def executemany(self, query: str, args_list: List[tuple]) -> None:
        """Execute a query multiple times with different parameters."""
        async with self.acquire() as conn:
            await conn.executemany(query, args_list)
    
    async def vector_search(
        self,
        embedding: List[float],
        table: str = "team_members",
        column: str = "skill_embedding",
        limit: int = 5,
        where_clause: str = "",
    ) -> List[Dict[str, Any]]:
        """
        Perform vector similarity search using pgvector cosine distance.
        
        Args:
            embedding: Query embedding vector
            table: Table to search in
            column: Vector column name
            limit: Max results to return
            where_clause: Optional additional WHERE conditions (e.g., "AND active = true")
            
        Returns:
            List of rows ordered by similarity (highest first), each with a 'similarity' field
        """
        # Convert embedding list to pgvector string format
        embedding_str = "[" + ",".join(str(x) for x in embedding) + "]"
        
        query = f"""
            SELECT *, 
                   1 - ({column} <=> $1::vector) AS similarity
            FROM {table}
            WHERE {column} IS NOT NULL {where_clause}
            ORDER BY {column} <=> $1::vector
            LIMIT $2
        """
        
        async with self.acquire() as conn:
            rows = await conn.fetch(query, embedding_str, limit)
            return [dict(row) for row in rows]


# Global database instance
db = Database()
