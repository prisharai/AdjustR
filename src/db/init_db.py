"""
Database initialization script
Creates all tables defined in models.py
"""
from src.db.database import engine, Base
from src.db.models import Video, Inference, Report
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_db():
    """Initialize database tables"""
    try:
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully!")

        # Log created tables
        logger.info("Created tables:")
        for table in Base.metadata.sorted_tables:
            logger.info(f"  - {table.name}")

    except Exception as e:
        logger.error(f"❌ Error creating database tables: {e}")
        raise


def drop_all_tables():
    """Drop all tables (use with caution!)"""
    logger.warning("⚠️  Dropping all database tables...")
    Base.metadata.drop_all(bind=engine)
    logger.info("All tables dropped")


if __name__ == "__main__":
    init_db()
