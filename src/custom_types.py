from datetime import datetime
from pydantic import BaseModel, field_validator, ValidationInfo
from pydantic import PositiveInt, Field

from my_tools import get_datetime_now, DateTimeKeys


class UserNotify(BaseModel):

    id: PositiveInt
    date: str = Field(default_factory=get_datetime_now)
    status: bool


class UserOnboarding(BaseModel):

    date: str = Field(default_factory=get_datetime_now, validate_default=True)
    approve: bool = Field(default=False)
    name: str | None = Field(default=None)
    important_today: str | None = Field(default=None)
    difficult_today: str | None = Field(default=None)
    something_else: str | None = Field(default=None)
    photo: str | None = Field(default=None)
    step_1: str | None = Field(default=None)
    background: str | None = Field(default=None)
    step_2: str | None = Field(default=None)
    step_3: str | None = Field(default=None)
    step_4: str | None = Field(default=None)
    step_5: str | None = Field(default=None)
    step_6: str | None = Field(default=None)

    @field_validator("date")
    @classmethod
    def set_date(cls, v: datetime):
        return get_datetime_now(DateTimeKeys.DEFAULT)


class UserOffboarding(BaseModel):

    date: str = Field(default_factory=get_datetime_now, validate_default=True)
    question_1: str | None = Field(default=None)
    question_2: str | None = Field(default=None)
    question_3: str | None = Field(default=None)
    question_4: str | None = Field(default=None)
    associate: str | None = Field(default=None)
    feedback: str | None = Field(default=None)

    @field_validator("date")
    @classmethod
    def set_date(cls, v: datetime):
        return get_datetime_now(DateTimeKeys.DEFAULT)


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
    full_name: str | None = Field(default=None)
    username: str | None = Field(default=None)
    is_premium: bool | None = Field(default=None)
    language_code: str = Field(default="")
    date: str = Field(default_factory=get_datetime_now)

    @field_validator("full_name", mode="before")
    @classmethod
    def set_fullname(cls, v: str | None, info: ValidationInfo) -> str | None:
        """Automatically generate full_name from first_name and last_name if not provided."""
        if v is not None:
            return v
        
        first_name = info.data.get("first_name")
        last_name = info.data.get("last_name")
        
        if first_name or last_name:
            return " ".join(filter(None, [first_name, last_name])).strip()
        
        return None

    @field_validator("username")
    @classmethod
    def set_username(cls, v: str | None) -> str | None:
        """Add Telegram URL prefix if username doesn't have it."""
        if v is None:
            return None
        
        if not v.startswith("https://t.me/"):
            return f"https://t.me/{v}"
        
        return v

    @field_validator("language_code")
    @classmethod
    def set_language_code(cls, v: str) -> str:
        """Ensure language_code is never None, default to empty string."""
        return v or ""

    def compare_fields(self) -> tuple:
        
        return (self.full_name, self.username, self.is_premium, self.language_code)
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, UserData):
            return NotImplemented
        return self.compare_fields() == other.compare_fields()
    
    def __hash__(self) -> int:
        """Make UserData hashable for use in sets and as dict keys."""
        return hash(self.compare_fields())