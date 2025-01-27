import pytest
from sqlmodel import select, func
from app.models import User
from app.exceptions import UserNotFound, UserPhoneNumberAlreadyExists


def test_create_and_read(db_instance_empty, session, user1):
    # Write User to DB
    db_instance_empty.create_user(user1, session)

    # # Read from DB
    user = db_instance_empty.get_user(user_id=1, session=session)
    assert user.first_name == user1.first_name
    assert user.phone_number == user1.phone_number

def test_integrity_error_handling(db_instance_empty, session, user1, user2):
    # Write User to DB
    db_instance_empty.create_user(user1, session)
    user2.phone_number = user1.phone_number

    with pytest.raises(UserPhoneNumberAlreadyExists):
        res = db_instance_empty.create_user(user2, session)



###  Для изучения SQLModel
def test_count(db_instance_empty, session, user1, user2):
    db_instance_empty.create_user(user1, session)
    statement = select(func.count()).select_from(User)
    number_of_users = session.exec(statement).one()
    assert number_of_users == 1

    db_instance_empty.create_user(user2, session)
    number_of_users = session.exec(statement).one()
    assert number_of_users == 2
#
# def test_read_all_tasks(db_instance_empty, session, task1, task2):
#     """
#     Test the reading of all tasks
#     """
#     # Write 2 Tasks to DB
#     db_instance_empty.create_task(task=task1, session=session)
#     db_instance_empty.create_task(task=task2, session=session)
#
#     # Read all Tasks from DB
#     tasks = db_instance_empty.read_tasks(session=session)
#     assert len(tasks) == 2
#     assert tasks[0].title == task1.title
#     assert tasks[1].title == task2.title
#
#
# def test_read_all_tasks_empty(db_instance_empty, session):
#     """
#     Test the reading of all tasks when the DB is empty
#     """
#     # Read all Tasks from DB
#     tasks = db_instance_empty.read_tasks(session=session)
#     assert len(tasks) == 0
#
#
# def test_delete_task(db_instance_empty, session, task1, task2):
#     """
#     Test the deletion of a task
#     """
#     # Write 2 Tasks to DB
#     db_instance_empty.create_task(task=task1, session=session)
#     db_instance_empty.create_task(task=task2, session=session)
#
#     # Delete Task
#     db_instance_empty.delete_task(session=session, task_id=1)
#
#     # Read Task from DB
#     with pytest.raises(TaskNotFoundError):
#         db_instance_empty.read_task(task_id=1, session=session)
#
#
# def test_delete_all_tasks(db_instance_empty, session, task1, task2):
#     """
#     Test the deletion of all tasks
#     """
#     # Write 2 Tasks to DB
#     db_instance_empty.create_task(task=task1, session=session)
#     db_instance_empty.create_task(task=task2, session=session)
#
#     # Delete all Tasks from DB
#     db_instance_empty.delete_all_tasks(session=session)
#
#     # Read all Tasks from DB
#     tasks = db_instance_empty.read_tasks(session=session)
#     assert len(tasks) == 0
#
#
# def test_update_task(db_instance_empty, session, task1):
#     """
#     Test the updating of a task (status)
#     """
#     # Write Task to DB
#     db_instance_empty.create_task(task=task1, session=session)
#
#     # Update Task
#     db_instance_empty.update_task(
#         session=session,
#         task_id=1,
#         task_status=TaskStatus.COMPLETED,
#         task_title="Wash The Car",  # Change from "Go to the Gym" to "Wash The Car"
#     )
#
#     # Read Task from DB
#     task = db_instance_empty.read_task(task_id=1, session=session)
#
#     # Check Task Status and Updated At
#     assert task.status == TaskStatus.COMPLETED
#     assert task.title == "Wash The Car"
#     assert task.updated_at > task.created_at
#
#     # Check that the description has not changed
#     assert task.description == task1.description
#
#
# def test_update_task_updated_at(db_instance_empty, session, task1):
#     """
#     Test the updating of a task (updated_at)
#     """
#     # Write Task to DB
#     db_instance_empty.create_task(task=task1, session=session)
#
#     # Update Task
#     db_instance_empty.update_task(
#         session=session,
#         task_id=1,
#         task_title="New Title",
#     )
#
#     # Read Task from DB
#     task = db_instance_empty.read_task(task_id=1, session=session)
#
#     # Check Task Updated At is greater than Created At
#     assert task.updated_at > task.created_at
