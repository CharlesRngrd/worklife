from app.api import add_app_routes
from app.db.session import get_db
from app.main import app

from fastapi.testclient import TestClient

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


def setup_environment():
    engine = create_engine(
        # TODO: Use a test DB for testing.
        "postgresql://dev:dev@worklife-test-db:5432/dev",
        poolclass=StaticPool,
    )

    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        except Exception:
            raise
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    add_app_routes(app)

    return TestClient(app)
