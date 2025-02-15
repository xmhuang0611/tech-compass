import logging
from typing import Any, Dict

from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings

logger = logging.getLogger(__name__)


class MongoDB:
    client: AsyncIOMotorClient = None
    db = None


db = MongoDB()


def get_mongodb_options() -> Dict[str, Any]:
    """Get MongoDB connection options including TLS/SSL if certificates are provided."""
    options = {
        "serverSelectionTimeoutMS": 5000  # 5 second timeout
    }

    # Add TLS/SSL options if certificates are provided
    if any(
        [
            settings.MONGODB_TLS_CERT_PATH,
            settings.MONGODB_TLS_CA_PATH,
            settings.MONGODB_TLS_KEY_PATH,
        ]
    ):
        options["tls"] = True

        if settings.MONGODB_TLS_CA_PATH:
            options["tlsCAFile"] = settings.MONGODB_TLS_CA_PATH

        if settings.MONGODB_TLS_CERT_PATH:
            options["tlsCertificateKeyFile"] = settings.MONGODB_TLS_CERT_PATH

        if settings.MONGODB_TLS_KEY_PATH:
            # Only used if the private key is in a separate file from the certificate
            options["tlsPrivateKeyFile"] = settings.MONGODB_TLS_KEY_PATH

        logger.info("TLS/SSL options enabled for MongoDB connection")

    return options


async def connect_to_mongo():
    try:
        logger.info(f"Connecting to MongoDB at {settings.MONGODB_URL}")
        options = get_mongodb_options()
        db.client = AsyncIOMotorClient(settings.MONGODB_URL, **options)
        # Verify the connection
        await db.client.server_info()
        db.db = db.client[settings.DATABASE_NAME]
        logger.info(f"Connected to MongoDB database: {settings.DATABASE_NAME}")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {str(e)}")
        raise


async def close_mongo_connection():
    try:
        if db.client is not None:
            db.client.close()
            logger.info("Closed MongoDB connection")
    except Exception as e:
        logger.error(f"Error closing MongoDB connection: {str(e)}")


def get_database():
    if db.db is None:
        raise RuntimeError("Database not initialized. Make sure to call connect_to_mongo() first.")
    return db.db
