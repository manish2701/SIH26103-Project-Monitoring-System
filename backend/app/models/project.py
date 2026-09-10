from datetime import date

from sqlalchemy import Date, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    department: Mapped[str] = mapped_column(String(150), nullable=False)
    location: Mapped[str] = mapped_column(String(150), nullable=False)

    project_type: Mapped[str] = mapped_column(String(100), nullable=False)

    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    expected_completion_date: Mapped[date] = mapped_column(Date, nullable=False)

    budget: Mapped[float] = mapped_column(Float, nullable=False)
    current_cost: Mapped[float] = mapped_column(Float, nullable=False)

    planned_progress: Mapped[float] = mapped_column(Float, nullable=False)
    actual_progress: Mapped[float] = mapped_column(Float, nullable=False)

    status: Mapped[str] = mapped_column(String(50), nullable=False)