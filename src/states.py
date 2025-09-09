from aiogram.fsm.state import State, StatesGroup


class Admin(StatesGroup):

    MAIN = State()


class Onboarding(StatesGroup):

    WELCOME = State()
    PREONBOARDING = State()
    NAME = State()
    IMPORTANT_TODAY = State()
    DIFFICULT_TODAY = State()
    SOMETHING_ELSE = State()
    PHOTO = State()
    NO_PHOTO = State()
    STEP_1 = State()
    BACKGROUND = State()
    STEP_2 = State()
    STEP_3 = State()
    STEP_4 = State()
    STEP_5 = State()
    STEP_6 = State()
    THANKS = State()


class Flow(StatesGroup):

    MENU = State()
    STUDENT_GALLERY = State()
    TEACHER_GALLERY = State()
    SCHEDULE = State()
    MY_PROFILE = State()


class StudentGallery(StatesGroup):

    SCROLL_LIST = State()
    PROFILE = State()
    EDIT_PROFILE = State()


class EditMode(StatesGroup):

    MAIN = State()
    EDIT_PHOTO = State()
    EDIT_NAME = State()
    EDIT_SLOGAN = State()
    EDIT_PROF_EXPERIENCE = State()
    EDIT_ABOUT = State()
    EDIT_TAGS = State()
    EDIT_EXPECTATIONS = State()