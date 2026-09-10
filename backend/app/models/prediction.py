from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class Prediction(Base):
    __tablename__ = "predictions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id"),
        nullable=False,
        index=True
    )

    predicted_cost: Mapped[float] = mapped_column(Float, nullable=False)

    cost_overrun_percentage: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    predicted_delay_days: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    risk_score: Mapped[float] = mapped_column(Float, nullable=False)

    risk_level: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )