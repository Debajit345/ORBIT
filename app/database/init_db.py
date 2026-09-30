from app.database.connection import Base, engine
from app.database import models


def init_database() -> None:
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_database()
    print("ORBIT database initialized successfully.")