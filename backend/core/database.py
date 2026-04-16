"""
Database connection and query utilities for AlloyDB.
"""
import asyncpg
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager
from .config import settings


class Database:
    """AlloyDB connection manager."""
    
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
    
    async def connect(self):
        """Create connection pool to AlloyDB."""
        if self.pool is None:
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
    
    async def disconnect(self):
        """Close connection pool."""
        if self.pool:
            await self.pool.close()
            self.pool = None
    
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


# Global database instance
db = Database()
