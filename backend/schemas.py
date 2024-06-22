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
