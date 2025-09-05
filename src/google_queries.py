from .utils.sheets_async import SheetsAsync


from .config import Config
from .custom_types import Teacher, Student


# Multiple singletons for different spreadsheets
_students_sheets_instance: SheetsAsync | None = None
_teachers_sheets_instance: SheetsAsync | None = None
_content_sheets_instance: SheetsAsync | None = None


def get_students_sheets_instance(config: Config) -> SheetsAsync:
    """
    Get or create a singleton SheetsAsync instance for students spreadsheet.
    """
    global _students_sheets_instance
    if _students_sheets_instance is None:
        _students_sheets_instance = SheetsAsync(
            spreadsheet_id = config.google.onboarding_id,
            sa_json_path = config.google.service_account_json
        )
    return _students_sheets_instance


def get_teachers_sheets_instance(config: Config) -> SheetsAsync:
    """
    Get or create a singleton SheetsAsync instance for teachers spreadsheet.
    """
    global _teachers_sheets_instance
    if _teachers_sheets_instance is None:
        _teachers_sheets_instance = SheetsAsync(
            spreadsheet_id = config.google.feedbacks_and_accesses_id,
            sa_json_path = config.google.service_account_json
        )
    return _teachers_sheets_instance



def get_content_sheets_instance(config: Config) -> SheetsAsync:
    """
    Get or create a singleton SheetsAsync instance for content spreadsheet.
    """
    global _content_sheets_instance
    if _content_sheets_instance is None:
        _content_sheets_instance = SheetsAsync(
            spreadsheet_id = config.google.content_id,  # Different spreadsheet
            sa_json_path = config.google.service_account_json
        )
    return _content_sheets_instance


async def get_students(config: Config) -> list[Student]:
    """
    Get list of students from Google Sheets.
    """
    sheet: SheetsAsync = get_students_sheets_instance(config)
    read_res = await sheet.read(f"{config.google.vitrina_tab}!A1:N")

    for ind, row in enumerate(read_res.get("values")[2:]):
        print(f"{ind+1}. {row}")

    students: list[Student] = [
        Student(id=row[0], name=row[1], slogan=row[6], prof_experience=row[7], about=row[8], tags=row[10], expectations=row[13])
        for row in read_res.get("values")[2:] if len(row) > 13]

    return sorted(students, key=lambda x: x.name.split()[1])


# Teachers spreadsheet operations
async def get_teachers(config: Config) -> list[Teacher]:
    """
    Get list of teachers from Google Sheets.
    """
    sheet: SheetsAsync = get_teachers_sheets_instance(config)

    read_res = await sheet.read(f"{config.google.accesses_tab}!A1:C{config.google.accesses_tab_length}")

    teachers: list[Teacher] = [
        Teacher(id=row[1], name=row[0], disciplines=row[2].split(", ")) 
        for row in read_res.get("values")[1:] if len(row) > 2]

    return teachers


async def get_teachers_ids(config: Config) -> set[int]:
    """
    Get list of teachers from Google Sheets.
    """

    teachers = await get_teachers(config)

    return set([teacher.id for teacher in teachers])


async def get_list_of_disciplines(
        config: Config, 
        teachers: list[Teacher],
        teacher_id: int) -> list[tuple[str, str]]:
    """
    Get list of disciplines for a current teacher.
    """

    sheet: SheetsAsync = get_teachers_sheets_instance(config)

    read_discs = await sheet.read(f"{config.google.accesses_tab}!E1:F{config.google.disciplines_tab_length}")

    discs = dict([(el[0], el[1]) for el in read_discs.get("values")[1:]])

    teacher = next((t for t in teachers if t.id == teacher_id), None)

    return [(d, discs.get(d)) for d in teacher.disciplines] # [("Матметоды", "mathmethods"), ...]


async def get_list_of_tasks(
        config: Config,
        disciplines: list[tuple[str, str]]) -> list[tuple[str, str]]:

    sheet: SheetsAsync = get_content_sheets_instance(config)

    task_data: dict = {}

    for discipline, disc_id in disciplines:
        read_tasks = await sheet.read(f"{disc_id}!A2:B")
        task_data[disc_id] = read_tasks.get("values")

    return task_data


async def get_syllabus(
        config: Config,
        disciplines: list[tuple[str, str]]) -> list[tuple[str, str]]:
    
    sheet: SheetsAsync = get_content_sheets_instance(config)
    read_syllabases = await sheet.read(f"{config.google.syllabus_tab}!A2:B")
    
    return read_syllabases.get("values")



async def get_start_data_for_dialog(
        config: Config,
        user_id: int) -> dict[str, dict[str, dict[str, str]]]:

    dialog_data: dict = {}

    students: list[Student] = await get_students(config)

    disciplines: list[tuple[str, str]] = await get_list_of_disciplines(config, teachers, user_id)
    syllabus: list[tuple[str, str]] = await get_syllabus(config, disciplines)
    tasks: list[tuple[str, str]] = await get_list_of_tasks(config, disciplines)

    for discipline, disc_id in disciplines:
        dialog_data[disc_id] = {
            "name": discipline,
            "syllabus": [el[1] for el in syllabus if el[0] == discipline][0]
            }

        for ind, task in enumerate(tasks[disc_id]):
            dialog_data[disc_id][f"task_{ind+1}"] = {
                "name": task[0],
                "description": task[1]}

    return dialog_data



async def put_feedback(
        config: Config,
        user_id: int,
        current_discipline_name: str,
        current_task_name: str,
        feedback: str):
    
    sheet: SheetsAsync = get_teachers_sheets_instance(config)

    await sheet.append(
        f"{user_id}!A1:C",
        [
            [current_discipline_name, current_task_name, feedback]
        ]
    )