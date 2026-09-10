from .database import Base, engine
from .models import (
    Project,
    Milestone,
    ProgressUpdate,
    Prediction,
    Alert,
)


def init_database():
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")


if __name__ == "__main__":
    init_database()