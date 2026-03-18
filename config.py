import os


DEFAULT_DATABASE_URL = (
    "postgresql://promotion_truck_platform_db_user:"
    "uqt2e6p00MxZA9NwwHeQTWVE1DNlVEdT@"
    "dpg-d6t2jvea2pns738hf2l0-a/promotion_truck_platform_db"
)


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-me")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)
    if SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "changeme123!")
