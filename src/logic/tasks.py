import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, date
from typing import List, Optional

from sqlalchemy import or_, and_, String, cast, not_
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from src.models.report_model import all_reports
from src.models.task_model_v2 import (
    Task,
    TaskFrequency,
    TaskStatusEnum,
    TaskSubjectTypeEnum,
    TaskFrequencyRepeatTypeEnum,
    TaskFrequencyWeekdayEnum,
    TaskTubTypeEnum,
)
from src.models.user_model import User
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TaskFrequencyData:
    id: Optional[int] = None
    repeat_count: Optional[int] = None
    repeat_type: TaskFrequencyRepeatTypeEnum = TaskFrequencyRepeatTypeEnum.UNLIMITED
    weekdays: Optional[List[TaskFrequencyWeekdayEnum]] = None

    def to_dict(self):
        return {
            "id": self.id,
            "repeat_count": self.repeat_count,
            "repeat_type": self.repeat_type.name if self.repeat_type else None,
            "weekdays": (
                [weekday.name for weekday in self.weekdays] if self.weekdays else None
            ),
        }


@dataclass
class TaskData:
    user_id: int
    subject_type: TaskSubjectTypeEnum
    tub_type: TaskTubTypeEnum
    subject_id: int
    name: str
    start_date: datetime
    id: Optional[uuid.UUID] = None
    description: Optional[str] = None
    status: TaskStatusEnum = TaskStatusEnum.TODO
    has_been_read: bool = False
    made_by_user: bool = False
    end_date: Optional[datetime] = None
    frequency: Optional[TaskFrequencyData] = None
    created_at: Optional[datetime] = None
    last_time_done: Optional[datetime] = None
    is_delete_from_notification: bool= False


    def to_dict(self):
        return {
            "user_id": str(self.user_id),
            "subject_type": self.subject_type.name,
            "subject_id": self.subject_id,
            "name": self.name,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "id": str(self.id),
            "description": self.description,
            "status": self.status.name,
            "has_been_read": self.has_been_read,
            "made_by_user": self.made_by_user,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "frequency": self.frequency.to_dict() if self.frequency else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "tub_type": self.tub_type.name,
            "last_time_done": self.last_time_done.isoformat() if self.last_time_done else None,
            "is_delete_from_notification": self.is_delete_from_notification

        }


class TaskNotFoundException(Exception):
    pass


class UserNotFoundException(Exception):
    pass


class InvalidTaskDataException(Exception):
    pass


class TaskService:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def get_all_tasks(self) -> List[dict]:
        logger.debug("Fetching all tasks")
        try:
            tasks = self.db_session.query(Task).all()
            logger.debug(f"Found {len(tasks)} tasks")
            return [self._task_to_data(task).to_dict() for task in tasks]
        except Exception as e:
            logger.error(f"Error fetching all tasks: {str(e)}")
            raise

    def get_events_by_subject_id(
        self, subject_id: str, subject_type: TaskSubjectTypeEnum, is_event
    ) -> List[dict]:
        logger.debug(
            f"Fetching tasks for subject with id {subject_id} and type {subject_type.name}"
        )
        try:
            too_old = datetime.today() - timedelta(days=7)
            too_new = datetime.today() + timedelta(days=3)
            if is_event and bool(is_event):
                tasks = (
                    self.db_session.query(Task)
                    .filter(
                        Task.subject_id == subject_id,
                        Task.subject_type == subject_type,
                        Task.name.notin_(all_reports),
                        Task.start_date >= too_old,
                        Task.start_date <= too_new,
                    )
                    .all()
                )
            else:
                tasks = (
                    self.db_session.query(Task)
                    .filter(
                        Task.subject_id == subject_id, Task.subject_type == subject_type
                    )
                    .all()
                )
            if not tasks:
                logger.warning(
                    f"No tasks found for subject with id {subject_id} and type {subject_type.name}"
                )
                return []
            logger.debug(
                f"Found {len(tasks)} tasks for subject with id {subject_id} and type {subject_type.name}"
            )
            return [self._task_to_data(task).to_dict() for task in tasks]
        except TaskNotFoundException:
            raise
        except Exception as e:
            logger.error(
                f"Error fetching tasks for subject with id {subject_id} and type {subject_type.name}: {str(e)}"
            )
            raise

    def get_task_by_id(self, task_id: uuid) -> dict:
        logger.debug(f"Fetching task with id {task_id}")
        try:
            task = self.db_session.query(Task).filter(Task.id == task_id).first()
            if not task:
                logger.warning(f"Task with id {task_id} not found")
                raise TaskNotFoundException(f"Task with id {task_id} not found")
            logger.debug(f"Found task: {task}")
            return self._task_to_data(task).to_dict()
        except TaskNotFoundException:
            raise
        except Exception as e:
            logger.error(f"Error fetching task with id {task_id}: {str(e)}")
            raise

    def get_tasks_by_user_id(self, user_id: int,is_contains_export) -> List[dict]:
        logger.debug(f"Fetching tasks for user with id {user_id}")
        try:
            tasks = (
                self.db_session.query(Task).filter(Task.user_id == user_id)
                #.filter(not_(and_(cast(Task.user_id,String()) == Task.subject_id,Task.made_by_user==False)))
                .all()#filter tasks about myself system made
            )
            if not tasks:
                logger.warning(f"No tasks found for user with id {user_id}")
                return []
            if is_contains_export and bool(is_contains_export):
                return [self._task_to_data(task).to_dict() for task in tasks]
            #if its a birthday or event : take -7<date<3
            #if its system report : filter out
            too_old = datetime.today() - timedelta(days=7)
            filtered_task_list = []
            for task_ in tasks:
                if "עידכון" in task_.name and task_.made_by_user == False:
                    continue
                if "דוח" in task_.name and task_.made_by_user == False:
                    continue
                three_days_old = task_.start_date + timedelta(days=3)
                if ("יום הולדת" == task_.name or task_.made_by_user == True) and (too_old>task_.start_date or datetime.today()>=three_days_old):
                    continue
                filtered_task_list.append(task_)
            logger.debug(f"Found {len(tasks)} tasks for user {user_id}")
            return [self._task_to_data(task).to_dict() for task in filtered_task_list]
        except UserNotFoundException:
            raise
        except Exception as e:
            logger.error(f"Error fetching tasks for user with id {user_id}: {str(e)}")
            raise

    def create_task(self, task_data: TaskData) -> dict:
        logger.debug(f"Creating new task: {task_data}")
        try:
            self._validate_user(task_data.user_id)
            task = Task(
                id=task_data.id,
                user_id=task_data.user_id,
                subject_type=task_data.subject_type,
                subject_id=task_data.subject_id,
                name=task_data.name,
                description=task_data.description,
                status=task_data.status,
                has_been_read=task_data.has_been_read,
                made_by_user=task_data.made_by_user,
                start_date=task_data.start_date,
                end_date=task_data.end_date,
                tub_type=task_data.tub_type,
                created_at=task_data.created_at,
            )

            if task.made_by_user:
                if not task_data.frequency:
                    raise InvalidTaskDataException(
                        "Frequency is required when task is made by user"
                    )
                frequency = self._create_frequency(task_data.frequency)
                self.db_session.add(frequency)
                self.db_session.flush()  # This will assign an ID to the frequency
                task.frequency_id = frequency.id
                if not task.end_date:
                    task.end_date = self._calculate_end_date(task.start_date, frequency)
            else:
                task.frequency_id = None
                task.end_date = None

            self.db_session.add(task)
            self.db_session.commit()
            logger.debug(f"Successfully created task with id {task.id}")
            return self._task_to_data(task).to_dict()
        except IntegrityError as e:
            self.db_session.rollback()
            logger.error(f"IntegrityError while creating task: {str(e)}")
            raise InvalidTaskDataException(f"Invalid task data provided: {str(e)}")
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Unexpected error while creating task: {str(e)}")
            raise

    def update_task(self, task_id: uuid, task_data: dict) -> dict:
        logger.debug(f"Updating task with id {task_id}: {task_data}")
        try:
            task = self.db_session.query(Task).filter(Task.id == task_id).first()
            if not task:
                logger.warning(f"Task with id {task_id} not found for update")
                raise TaskNotFoundException(f"Task with id {task_id} not found")

            # Update only the fields provided in task_data
            for field, value in task_data.items():
                if field != "frequency" and value is not None:
                    if field == "subject_type" and isinstance(
                        value, TaskSubjectTypeEnum
                    ):
                        setattr(task, field, value)
                    elif field == "status" and isinstance(value, TaskStatusEnum):
                        setattr(task, field, value)
                    elif hasattr(task, field):
                        setattr(task, field, value)

            if "frequency" in task_data and task.made_by_user:
                self._update_frequency(task, task_data["frequency"])
                if not task_data.get("end_date"):
                    task.end_date = self._calculate_end_date(
                        task.start_date, task.frequency
                    )

            self.db_session.commit()
            logger.debug(f"Successfully updated task with id {task_id}")
            return self._task_to_data(task).to_dict()
        except TaskNotFoundException:
            raise
        except IntegrityError as e:
            self.db_session.rollback()
            logger.error(f"IntegrityError while updating task: {str(e)}")
            raise InvalidTaskDataException(f"Invalid task data provided: {str(e)}")
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Unexpected error while updating task: {str(e)}")
            raise

    def delete_task(self, task_id: uuid) -> None:
        logger.debug(f"Deleting task with id {task_id}")
        try:
            task = self.db_session.query(Task).filter(Task.id == task_id).first()
            if not task:
                logger.warning(f"Task with id {task_id} not found for deletion")
                raise TaskNotFoundException(f"Task with id {task_id} not found")
            self.db_session.delete(task)
            self.db_session.commit()
            logger.debug(f"Successfully deleted task with id {task_id}")
        except TaskNotFoundException:
            raise
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Error deleting task with id {task_id}: {str(e)}")
            raise

    def _validate_user(self, user_id: int) -> None:
        logger.debug(f"Validating user with id {user_id}")
        user = self.db_session.query(User).filter(User.id == user_id).first()
        if not user:
            logger.warning(f"User with id {user_id} not found")
            raise UserNotFoundException(f"User with id {user_id} not found")
        logger.debug(f"User with id {user_id} is valid")

    def _create_frequency(self, frequency_data: TaskFrequencyData) -> TaskFrequency:
        logger.debug(f"Creating frequency: {frequency_data.weekdays}")
        frequency = TaskFrequency(
            repeat_count=frequency_data.repeat_count,
            repeat_type=frequency_data.repeat_type,
        )
        if frequency.repeat_type == TaskFrequencyRepeatTypeEnum.WEEKLY:
            frequency.weekdays = frequency_data.weekdays
        return frequency

    def _update_frequency(self, task: Task, frequency_data: TaskFrequencyData) -> None:
        logger.debug(f"Updating frequency for task {task.id}: {frequency_data}")
        if not task.frequency:
            task.frequency = self._create_frequency(frequency_data)
        else:
            task.frequency.repeat_count = frequency_data.repeat_count
            task.frequency.repeat_type = frequency_data.repeat_type
            if frequency_data.repeat_type == TaskFrequencyRepeatTypeEnum.WEEKLY:
                task.frequency.weekdays = frequency_data.weekdays
            else:
                task.frequency.weekdays = None

    def _calculate_end_date(
        self, start_date: datetime, frequency: TaskFrequency
    ) -> Optional[datetime]:
        logger.debug(
            f"Calculating end date for start date {start_date} and frequency {frequency}"
        )
        if frequency.repeat_type == TaskFrequencyRepeatTypeEnum.UNLIMITED:
            return None

        if frequency.repeat_count is None:
            return None

        if frequency.repeat_type == TaskFrequencyRepeatTypeEnum.DAILY:
            end_date = start_date + timedelta(days=frequency.repeat_count)
        elif frequency.repeat_type == TaskFrequencyRepeatTypeEnum.WEEKLY:
            end_date = start_date + timedelta(weeks=frequency.repeat_count)
        elif frequency.repeat_type == TaskFrequencyRepeatTypeEnum.MONTHLY:
            end_date = start_date + timedelta(days=30 * frequency.repeat_count)
        elif frequency.repeat_type == TaskFrequencyRepeatTypeEnum.YEARLY:
            end_date = start_date + timedelta(days=365 * frequency.repeat_count)
        else:
            end_date = None

        logger.debug(f"Calculated end date: {end_date}")
        return end_date

    def _task_to_data(self, task: Task) -> TaskData:
        logger.debug(f"Converting task to TaskData: {task}")
        frequency_data = None
        if task.frequency:
            frequency_data = TaskFrequencyData(
                id=task.frequency.id,
                repeat_count=task.frequency.repeat_count,
                repeat_type=task.frequency.repeat_type,
                weekdays=task.frequency.weekdays if task.frequency.weekdays else None,
            )
        return TaskData(
            id=task.id,
            user_id=task.user_id,
            subject_type=task.subject_type,
            subject_id=task.subject_id,
            name=task.name,
            description=task.description,
            status=task.status,
            has_been_read=task.has_been_read,
            made_by_user=task.made_by_user,
            start_date=task.start_date,
            end_date=task.end_date,
            frequency=frequency_data,
            created_at=task.created_at,
            tub_type=task.tub_type,
            last_time_done=task.last_time_done,
            is_delete_from_notification=task.is_delete_from_notification,

        )


class TaskFactory:
    @staticmethod
    def create_task_service(db_session: Session) -> TaskService:
        logger.debug("Creating new TaskService instance")
        return TaskService(db_session)
