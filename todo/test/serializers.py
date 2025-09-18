# test/serializers.py
from ninja import Schema
from typing import Optional
from datetime import date

class RegisterSchema(Schema):
    email: str
    password: str

class LoginSchema(Schema):
    email: str
    password: str

class TodoSchema(Schema):
    title: str
    description: Optional[str]
    start_date: date
    end_date: date
    status: str  # "todo", "inprogress", "done"

class TodoUpdateSchema(Schema):
    title: Optional[str]
    description: Optional[str]
    start_date: Optional[date]
    end_date: Optional[date]
    status: Optional[str]
