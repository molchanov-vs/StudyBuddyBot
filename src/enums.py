from enum import Enum


class ButtonsId(str, Enum):
    
    EDIT_PHOTO_BTN_ID = "edit_photo_btn_id"
    EDIT_NAME_BTN_ID = "edit_name_btn_id"
    EDIT_SLOGAN_BTN_ID = "edit_slogan_btn_id"
    EDIT_PROF_EXPERIENCE_BTN_ID = "edit_prof_experience_btn_id"
    EDIT_ABOUT_BTN_ID = "edit_about_btn_id"
    EDIT_TAGS_BTN_ID = "edit_tags_btn_id"
    EDIT_EXPECTATIONS_BTN_ID = "edit_expectations_btn_id"
    EDIT_MISSION_BTN_ID = "edit_mission_btn_id"


class Action(str, Enum):
    
    START = "start"
    RESTART = "restart"
    BACK = "back"
    NEXT = "next"
    CANCEL = "cancel"
    CONFIRM = "confirm"
    DELETE = "delete"
    EDIT = "edit"
    SEND = "send"
    SELECT = "select"
    SELECTED = "selected"
    UNSELECTED = "unselected"
    ADD = "add"
    REMOVE = "remove"
    ONBOARDING = "onboarding"
    OFFBOARDING = "offboarding"
    CHAT = "chat"


class Database(str, Enum):

    FSM = "fsm"
    USERS = "users"
    TEMP = "temp"


class RedisKeys(str, Enum):

    KNOWN_USERS = "known_users"
    TEACHERS = "teachers"
    STUDENTS = "students"
    FOR_ONBOARDING = "for_onboarding"