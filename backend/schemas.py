from typing import Optional, Union

from pydantic import BaseModel, ConfigDict, Field, ValidationError


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
    phone_number: Optional[str] = Field(
        min_length=10, max_length=11, default="09000000000"
    )


class Token(BaseModel):
    access_token: str
    token_type: str


class UserVerificationPassword(BaseModel):
    password: str
    new_password: str = Field(min_length=6, max_length=255)


class UserVerificationPhoneNumber(BaseModel):
    phone_number: str = Field(
        min_length=10,
        max_length=11,
        pattern="^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$",
    )
