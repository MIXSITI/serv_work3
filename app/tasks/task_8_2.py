"""
Задание 8.2 (ТЗ).

Модель Todo (id, title, description, completed); CRUD без SQLAlchemy (raw SQL):
POST /todos, GET /todos/{id}, PUT /todos/{id}, DELETE /todos/{id}.
"""
from __future__ import annotations

import sqlite3

from fastapi import APIRouter, Depends, HTTPException, status

from app.tasks.task_8_1 import get_db
from app.schemas import Message, Todo, TodoCreate, TodoUpdate


def init_todos_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL DEFAULT '',
            completed INTEGER NOT NULL DEFAULT 0
        )
        """
    )


router = APIRouter(tags=["8.2 Todo CRUD"])


@router.post("/todos", response_model=Todo, status_code=status.HTTP_201_CREATED)
def create_todo(
    body: TodoCreate,
    db: sqlite3.Connection = Depends(get_db),
) -> Todo:
    cur = db.cursor()
    cur.execute(
        "INSERT INTO todos (title, description, completed) VALUES (?, ?, 0)",
        (body.title, body.description),
    )
    db.commit()
    tid = cur.lastrowid
    cur.execute("SELECT id, title, description, completed FROM todos WHERE id = ?", (tid,))
    row = cur.fetchone()
    assert row is not None
    return Todo(
        id=row["id"],
        title=row["title"],
        description=row["description"],
        completed=bool(row["completed"]),
    )


@router.get("/todos/{todo_id}", response_model=Todo)
def get_todo(
    todo_id: int,
    db: sqlite3.Connection = Depends(get_db),
) -> Todo:
    cur = db.cursor()
    cur.execute(
        "SELECT id, title, description, completed FROM todos WHERE id = ?",
        (todo_id,),
    )
    row = cur.fetchone()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    return Todo(
        id=row["id"],
        title=row["title"],
        description=row["description"],
        completed=bool(row["completed"]),
    )


@router.put("/todos/{todo_id}", response_model=Todo)
def update_todo(
    todo_id: int,
    body: TodoUpdate,
    db: sqlite3.Connection = Depends(get_db),
) -> Todo:
    cur = db.cursor()
    cur.execute("SELECT id FROM todos WHERE id = ?", (todo_id,))
    if cur.fetchone() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    fields: list[str] = []
    values: list[object] = []
    if body.title is not None:
        fields.append("title = ?")
        values.append(body.title)
    if body.description is not None:
        fields.append("description = ?")
        values.append(body.description)
    if body.completed is not None:
        fields.append("completed = ?")
        values.append(1 if body.completed else 0)
    if not fields:
        cur.execute(
            "SELECT id, title, description, completed FROM todos WHERE id = ?",
            (todo_id,),
        )
        row = cur.fetchone()
        assert row is not None
        return Todo(
            id=row["id"],
            title=row["title"],
            description=row["description"],
            completed=bool(row["completed"]),
        )
    values.append(todo_id)
    cur.execute(
        f"UPDATE todos SET {', '.join(fields)} WHERE id = ?",
        values,
    )
    db.commit()
    cur.execute(
        "SELECT id, title, description, completed FROM todos WHERE id = ?",
        (todo_id,),
    )
    row = cur.fetchone()
    assert row is not None
    return Todo(
        id=row["id"],
        title=row["title"],
        description=row["description"],
        completed=bool(row["completed"]),
    )


@router.delete("/todos/{todo_id}", response_model=Message)
def delete_todo(
    todo_id: int,
    db: sqlite3.Connection = Depends(get_db),
) -> Message:
    cur = db.cursor()
    cur.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
    if cur.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    db.commit()
    return Message(message="Todo deleted successfully")
