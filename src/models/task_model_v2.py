import uuid
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
    CheckConstraint,
)
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy.dialects.postgresql import ARRAY

from src.models.report_model import *
from src.services import db
from src.models.user_model import User


class TaskTubTypeEnum(PyEnum):
    PERSONAL = 1
    GENERAL = 2
    CALL = 3
    MEET = 4
    PARENTS = 5
    NOTIFICATION_ONLY = 6


class TaskSubjectTypeEnum(PyEnum):
    USER = 1
    INSTITUTION = 2
    APPRENTICE = 3


class TaskStatusEnum(PyEnum):
    TODO = 1
    DRAFT = 2
    DONE = 3


class TaskFrequencyWeekdayEnum(PyEnum):
    SUNDAY = 6
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5


class TaskFrequencyRepeatTypeEnum(PyEnum):
    DAILY = 1
    WEEKLY = 2
    MONTHLY = 3
    YEARLY = 4
    UNLIMITED = 5


class TaskFrequency(db.Model):
    __tablename__ = "task_frequency"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    repeat_count = Column(Integer(), nullable=True)
    repeat_type = Column(Enum(TaskFrequencyRepeatTypeEnum), nullable=False)
    weekdays = Column(ARRAY(Enum(TaskFrequencyWeekdayEnum)), nullable=True)

    tasks = relationship("Task", back_populates="frequency")

    __table_args__ = (
        CheckConstraint("(repeat_type = 'WEEKLY') = (weekdays IS NOT NULL)"),
    )

    def __repr__(self):
        return f"<TaskFrequency(id={self.id}, repeat_type='{self.repeat_type}', repeat_count={self.repeat_count})>"


class Task(db.Model):
    __tablename__ = "tasks"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    user_id = mapped_column(ForeignKey(User.id), nullable=False)
    subject_type = Column(Enum(TaskSubjectTypeEnum), nullable=False)
    subject_id = Column(Integer(), nullable=False)
    tub_type = Column(Enum(TaskTubTypeEnum), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    status = Column(Enum(TaskStatusEnum), nullable=False, default=TaskStatusEnum.TODO)
    has_been_read = Column(Boolean(), nullable=False, default=False)
    made_by_user = Column(Boolean(), nullable=False, default=False)
    is_delete_from_notification = Column(Boolean(), nullable=False, default=False)
    frequency_id = mapped_column(ForeignKey(TaskFrequency.id), nullable=True)
    created_at: Mapped[DateTime] = Column(
        DateTime(),
        nullable=False,
    )
    start_date: Mapped[DateTime] = Column(DateTime(), nullable=False)
    end_date: Mapped[DateTime] = Column(DateTime(), nullable=True)
    last_time_done: Mapped[DateTime] = Column(DateTime(), nullable=False)

    user = relationship("User", back_populates="tasks")
    frequency = relationship("TaskFrequency", back_populates="tasks")

    __table_args__ = (CheckConstraint("(subject_type IS NULL) = (subject_id IS NULL)"),)

    def __repr__(self):
        return f"<Task(id={self.id}, name='{self.name}', status='{self.status}')>"


# Add this to User model if not already present
User.tasks = relationship("Task", back_populates="user")



