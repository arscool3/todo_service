from sqlalchemy.orm import Session

from todo import schemas, models


def create_todo(db: Session, todo: schemas.TodoCreate):
    db_todo = models.Todo(title=todo.title, description=todo.description)

    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)

    return db_todo


def get_todo(db: Session, todo_id: int):
    return db.query(models.Todo).filter(models.Todo.id == todo_id).first()


def get_todos(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Todo).offset(skip).limit(limit).all()


def update_todo(db: Session, todo_id: int, todo: schemas.TodoUpdate):
    db_todo = get_todo(db, todo_id)

    db_todo.title = todo.title
    db_todo.description = todo.description

    db.commit()
    db.refresh(db_todo)

    return db_todo


def delete_todo(db: Session, todo_id: int):
    db_todo = get_todo(db, todo_id)
    db.delete(db_todo)
    db.commit()
