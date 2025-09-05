from pydantic import BaseModel, field_validator, ValidationInfo
from pydantic import PositiveInt, Field
from typing import Any
import re

from my_tools import get_datetime_now


class Student(BaseModel):

    id: PositiveInt
    name: str
    slogan: str | None = Field(default=None)
    prof_experience: str | None = Field(default=None)
    about: str | None = Field(default=None)
    tags: list[str] | None = Field(default=None)
    expectations: str | None = Field(default=None)

    @field_validator("tags", mode="before")
    @classmethod
    def parse_tags(cls, v: Any):

        if v is None:
            return None

        parts: list[str] = []

        if isinstance(v, str):
            parts = re.split(r"[,\n]+", v)
        elif isinstance(v, list):
            for item in v:
                if isinstance(item, str):
                    parts.extend(re.split(r"[,\n]+", item))
                elif item is not None:
                    parts.append(str(item))
        else:
            return v

        cleaned = [s.strip().lower() for s in parts if isinstance(s, str) and s.strip()]
        return cleaned or None


class Teacher(BaseModel):

    id: PositiveInt
    name: str


class UserNotify(BaseModel):

    id: PositiveInt
    date: str = Field(default_factory=get_datetime_now)
    status: bool


class UserAction(BaseModel):

    date: str = Field(default_factory=get_datetime_now)
    action_id: str


class MessageForGPT(BaseModel):

    date: str = Field(default_factory=get_datetime_now)
    state: str
    text: str


class UserData(BaseModel):

    id: PositiveInt
    first_name: str | None = Field(default=None)
    last_name: str | None = Field(default=None)
    full_name: str | None = Field(default=None, validate_default=True)
    username: str | None = Field(default=None)
    is_premium: bool | None = Field(default=None)
    language_code: str = Field(default="")
    date: str = Field(default_factory=get_datetime_now)


    @field_validator("full_name", mode="before")
    @classmethod
    def set_fullname(cls, v: str, info: ValidationInfo):

        _first_name = info.data.get("first_name")
        _last_name = info.data.get("last_name")

        if _first_name or _last_name:
            _full_name = " ".join(
                [
                    _first_name if _first_name else "", 
                    _last_name if _last_name else ""
                ]).strip()
        else:
            _full_name = v
        
        return _full_name 


    @field_validator("username")
    @classmethod
    def set_username(cls, v: str):

        if isinstance(v, str) and not v.startswith("https://t.me/"):
            return f"https://t.me/{v}"
        else:
            return v


    @field_validator("language_code", mode="before")
    @classmethod
    def set_language_code(cls, v: str):

        if not v:
            return ""
        else:
            return v

    def compare_fields(self) -> tuple:
        
        return (self.full_name, self.username, self.is_premium, self.language_code)
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, UserData):
            return NotImplemented
        return self.compare_fields() == other.compare_fields()
