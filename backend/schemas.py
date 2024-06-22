from pydantic import BaseModel, ValidationError, Field, ConfigDict
from typing import Optional, Union


class TodosRequest(BaseModel):
    title: str = Field(min_length=3)
    description: Optional[str] = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    completed: bool = False

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "a new task",
                "description": "task description",
                "priority": 5,
                "completed": False,
            }
        }
    }



class CreateUserRequest(BaseModel):
    username: str = Field(min_length=3, max_length=20)
    email: str = Field(min_length=6, max_length=100)
    first_name: str = Field(min_length=3, max_length=20)
    last_name: str = Field(min_length=3, max_length=20)
    password: str = Field(min_length=6, max_length=255)
    role: str = Field(min_length=3)