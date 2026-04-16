"""
Configuration management for Tech Sarathi backend.
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # GCP Configuration
    google_cloud_project: str = "nirman-project-493414"
    google_cloud_region: str = "asia-south1"
    google_application_credentials: str = "./service-account.json"
    
    # AlloyDB Configuration (raw connection - for local dev)
    alloydb_host: str = "localhost"
    alloydb_database: str = "sarathi"
    alloydb_user: str = "postgres"
    alloydb_password: str = "postgres"
    alloydb_port: int = 5432
    
    # AlloyDB Connector Configuration (for production)
    alloydb_use_connector: bool = False
    alloydb_instance_uri: str = "projects/nirman-project-493414/locations/asia-south1/clusters/sarathi-cluster/instances/sarathi-primary"
    alloydb_iam_auth: bool = False
    
    # AI Configuration
    gemini_model: str = "gemini-2.0-flash"
    gemini_api_key: str = ""
    
    # Vertex AI Embedding Configuration
    vertex_ai_embedding_model: str = "text-embedding-004"
    vertex_ai_embedding_dimensions: int = 768
    
    # Confidence Thresholds
    confidence_auto_threshold: float = 0.85
    confidence_escalate_threshold: float = 0.65
    
    # ReAct Loop Configuration
    react_loop_interval_seconds: int = 300
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = True
    
    # CORS
    cors_origins: str = "http://localhost:5173,http://localhost:3000"
    
    # Environment
    environment: str = "development"
    
    @property
    def cors_origins_list(self):
        """Parse CORS origins string into list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
