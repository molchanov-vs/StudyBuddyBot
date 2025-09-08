from pydantic import BaseModel, field_validator, ValidationInfo, HttpUrl
from pydantic import PositiveInt, Field
from typing import Any
import re
import logging

from my_tools import get_datetime_now

# Set up logger for this module
logger = logging.getLogger(__name__)


class Student(BaseModel):

    id: PositiveInt
    name: str
    username: HttpUrl | str = Field(default="")
    slogan: str | None = Field(default=None)
    prof_experience: str | None = Field(default=None)
    about: str | None = Field(default=None)
    tags: list[str] | None = Field(default=None)
    expectations: str | None = Field(default=None)
    image_file_id: str | None = Field(default=None)
    image_path: str | None = Field(default=None)

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
    
    def get_display_name(self) -> str:
        """
        Returns the name in format "Vova M." (first name + first letter of surname)
        """
        name_parts = self.name.strip().split()
        
        if not name_parts:
            return ""
        
        first_name = name_parts[0]
        
        if len(name_parts) > 1:
            # Get first letter of surname and add period
            surname_initial = name_parts[-1][0].upper() + "."
            return f"{first_name} {surname_initial}"
        else:
            # Only first name available
            return first_name


    def get_latest_image_path(self, all_images: list[str]):

        filtered_images: list[str] = [
            image 
            for image in all_images 
            if f"{self.id}" in image
        ]
        
        if filtered_images:
            self.image_path = filtered_images[-1]
        else:
            self.image_path = None

    def count_characters(self, text: str | None) -> int:
        """Count characters in a text string."""
        if not text or not isinstance(text, str):
            return 0
        return len(text)

    def get_total_character_count(self) -> int:
        """Get total character count for all text fields."""
        text_fields = [self.slogan, self.prof_experience, self.about, self.expectations]
        total_chars = sum(self.count_characters(field) for field in text_fields)
        
        # Log individual field character counts for debugging
        field_counts = {
            'slogan': self.count_characters(self.slogan),
            'prof_experience': self.count_characters(self.prof_experience),
            'about': self.count_characters(self.about),
            'expectations': self.count_characters(self.expectations)
        }
        
        logger.debug(f"Student {self.id} {self.name} character counts: {field_counts}, total: {total_chars}")
        return total_chars

    def truncate_text_to_character_limit(self, text: str | None, max_chars: int) -> str | None:
        """Truncate text to a maximum number of characters."""
        if not text or not isinstance(text, str):
            return text
        
        if len(text) <= max_chars:
            return text
        
        # Log truncation event
        original_char_count = len(text)
        logger.info(f"Truncating text from {original_char_count} characters to {max_chars} characters")
        
        # Truncate and add ellipsis if needed
        truncated_text = text[:max_chars-3] + "..."
        
        logger.debug(f"Truncated text preview: {truncated_text[:100]}...")
        return truncated_text

    def apply_character_limit(self, max_total_chars: int = 3500):
        """Apply character limit by truncating the longest text fields."""
        current_total = self.get_total_character_count()
        
        if current_total <= max_total_chars:
            logger.debug(f"Student {self.id} character count ({current_total}) is within limit ({max_total_chars})")
            return  # No truncation needed
        
        logger.warning(f"Student {self.id} exceeds character limit: {current_total} > {max_total_chars}. Applying truncation.")
        
        # Get text fields with their character counts
        text_fields = {
            'slogan': self.slogan,
            'prof_experience': self.prof_experience,
            'about': self.about,
            'expectations': self.expectations
        }
        
        # Sort fields by character count (descending)
        field_char_counts = [(field, self.count_characters(text)) for field, text in text_fields.items()]
        field_char_counts.sort(key=lambda x: x[1], reverse=True)
        
        # Calculate how many characters we need to remove
        chars_to_remove = current_total - max_total_chars
        logger.info(f"Need to remove {chars_to_remove} characters from Student {self.id}")
        
        # Log which fields will be truncated
        fields_to_truncate = [(field, count) for field, count in field_char_counts if count > 0]
        logger.info(f"Fields to truncate (in order): {fields_to_truncate}")
        
        # Truncate fields starting with the longest ones
        for field_name, char_count in field_char_counts:
            if chars_to_remove <= 0:
                break
                
            if char_count > 0:
                # Calculate how many characters to keep for this field
                chars_to_keep = max(0, char_count - chars_to_remove)
                
                # Truncate the field
                current_text = text_fields[field_name]
                if current_text:
                    logger.info(f"Truncating field '{field_name}' from {char_count} to {chars_to_keep} characters")
                    setattr(self, field_name, self.truncate_text_to_character_limit(current_text, chars_to_keep))
                    chars_to_remove -= (char_count - chars_to_keep)
        
        # Log final character count after truncation
        final_total = self.get_total_character_count()
        logger.info(f"Student {self.id} character count after truncation: {final_total}")

    def validate_and_apply_character_limits(self, max_total_chars: int = 3500) -> bool:
        """
        Manually validate and apply character limits to the Student instance.
        Returns True if truncation was applied, False if no changes were needed.
        """
        current_total = self.get_total_character_count()
        
        if current_total <= max_total_chars:
            logger.debug(f"Student {self.id} character count ({current_total}) is within limit ({max_total_chars})")
            return False
        
        logger.warning(f"Student {self.id} exceeds character limit: {current_total} > {max_total_chars}. Applying truncation.")
        self.apply_character_limit(max_total_chars)
        return True

    def validate_for_message(self) -> bool:
        """
        Validate for regular message (4096 char limit).
        Returns True if truncation was applied, False if no changes were needed.
        """
        return self.validate_and_apply_character_limits(3500)  # Leave buffer under 4096

    def get_formatted_caption_components(self) -> dict[str, str]:
        """
        Get the formatted caption components as a dictionary.
        Useful for dialog templates and debugging.
        """
        return {
            "student_slogan": f"\n<i>{self.slogan}</i>" if self.slogan else "",
            "student_about": f"\n📍О себе:\n{self.about}" if self.about else "",
            "student_prof_experience": f"\n📍Профессиональный опыт:\n{self.prof_experience}" if self.prof_experience else "",
            "student_expectations": f"\nНа программе ищу/ожидаю:\n{self.expectations}" if self.expectations else "",
        }

    def get_formatted_caption(self) -> str:
        """
        Get the actual formatted caption text that will be sent to Telegram,
        including all dialog formatting.
        """
        components = self.get_formatted_caption_components()
        return components["student_slogan"] + components["student_about"] + components["student_prof_experience"] + components["student_expectations"]

    def get_validated_formatted_caption(self, max_length: int = 950) -> str:
        """
        Get formatted caption that is guaranteed to be within character limits.
        Applies truncation if needed to ensure the caption fits.
        """
        # First, validate and truncate the student data if needed
        current_formatted_length = self.calculate_formatted_caption_length()
        
        if current_formatted_length > max_length:
            # Calculate how much we need to reduce the content
            excess = current_formatted_length - max_length
            current_content_length = self.get_total_character_count()
            target_content_length = max(0, current_content_length - excess)
            
            # Apply character limit to reduce content by the excess amount
            self.validate_and_apply_character_limits(target_content_length)
        
        # Return the formatted caption (now guaranteed to be within limits)
        return self.get_formatted_caption()

    def calculate_formatted_caption_length(self) -> int:
        """
        Calculate the actual caption length that will be sent to Telegram,
        including all dialog formatting.
        """
        return len(self.get_formatted_caption())

    def validate_for_caption(self) -> bool:
        """
        Validate for media caption (1024 char limit).
        Calculates exact formatting overhead and adjusts accordingly.
        Returns True if truncation was applied, False if no changes were needed.
        """
        max_caption_length = 1000  # Leave buffer under 1024
        
        # Check if current formatted caption exceeds limit
        current_formatted_length = self.calculate_formatted_caption_length()
        
        if current_formatted_length <= max_caption_length:
            logger.debug(f"Student {self.id} formatted caption length ({current_formatted_length}) is within limit ({max_caption_length})")
            return False
        
        logger.warning(f"Student {self.id} formatted caption too long: {current_formatted_length} > {max_caption_length}. Applying truncation.")
        
        # Calculate how much we need to reduce the content
        excess = current_formatted_length - max_caption_length
        
        # Apply character limit to reduce content by the excess amount
        current_content_length = self.get_total_character_count()
        target_content_length = max(0, current_content_length - excess)
        
        return self.validate_and_apply_character_limits(target_content_length)


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
