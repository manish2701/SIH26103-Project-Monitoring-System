from datetime import date

from sqlalchemy import Date, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class ProgressUpdate(Base):
    __tablename__ = "progress_updates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id"),
        nullable=False,
        index=True
    )

    update_date: Mapped[date] = mapped_column(Date, nullable=False)

    progress: Mapped[float] = mapped_column(Float, nullable=False)

    cost: Mapped[float] = mapped_column(Float, nullable=False)

    remarks: Mapped[str | None] = mapped_column(Text, nullable=True)