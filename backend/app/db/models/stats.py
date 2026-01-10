"""DailyStats database model."""

from datetime import datetime, date
from sqlalchemy import Column, Integer, DateTime, Date, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4

from app.db.session import Base


class DailyStats(Base):
    """DailyStats model for tracking daily character metrics."""

    __tablename__ = "daily_stats"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    character_id = Column(UUID(as_uuid=True), ForeignKey("characters.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False, index=True)

    # Daily metrics
    tasks_completed = Column(Integer, default=0, nullable=False)
    rituals_completed = Column(Integer, default=0, nullable=False)
    abilities_used = Column(Integer, default=0, nullable=False)
    experience_gained = Column(Integer, default=0, nullable=False)
    gold_earned = Column(Integer, default=0, nullable=False)

    # Health tracking
    health_lost = Column(Integer, default=0, nullable=False)
    health_restored = Column(Integer, default=0, nullable=False)

    # Time tracking
    active_time_minutes = Column(Integer, default=0, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("character_id", "date", name="unique_character_date"),
    )

    def __repr__(self):
        return f"<DailyStats {self.character_id} on {self.date}>"
