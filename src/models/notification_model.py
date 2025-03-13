import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import (
    ForeignKey,
    Enum,
    Column,
    Integer,
    Boolean,
    String,
    DateTime,
    func,
    CheckConstraint, UUID,
)
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy.dialects.postgresql import ARRAY

from src.models import to_iso
from src.models.report_model import *
from src.models.system_report_model import *
from src.services import db
from src.models.user_model import User

class notifications(db.Model):
    __tablename__ = "notifications"
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = mapped_column(ForeignKey(User.id), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    has_been_read = Column(Boolean(), nullable=False, default=False)
    created_at: Mapped[DateTime] = Column(
        DateTime(),
        default=datetime.now().strftime("%Y%m%d %H%M%S"),
        nullable=False,
    )


    def to_attributes(self):
        return {
            "id": str(self.id),
            "name": str(self.name),
            "user_id": str(self.user_id),
            "description": self.description,
            "has_been_read": self.has_been_read,
            "creation_date": str(self.created_at),
        }

notification_schedule_dict = {

    call_report: "week",
    personalMeet_report: "week",
    groupMeet_report: "week",
    basis_report: "rivon",
    HorimCall_report: "elul",

    matzbar_report: "2week",
    hazanatMachzor_report: "elul",
    doForBogrim_report: "month",
    professional_report: "month",
    MelavimMeeting_report: "2week",

    MOsadEshcolMeeting_report: "2week",
    tochnitMeeting_report: "2week",
    cenes_report: "rivon",
forgotenApprentice_list : "2week",
melave_Score_list : "month",
low_score_65_list : "month",
mosdot_score_list : "month"

}