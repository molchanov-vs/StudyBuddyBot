from .utils.sheets_async import SheetsAsync


from .config import Config
from .custom_types import Teacher, Student

from pprint import pprint


# Multiple singletons for different spreadsheets
_main_sheets_instance: SheetsAsync | None = None

async def get_main_sheets_instance(config: Config, rng: str) -> list[list[str]]:
    """
    Get or create a singleton SheetsAsync instance for students spreadsheet.
    """
    global _main_sheets_instance
    if _main_sheets_instance is None:
        _main_sheets_instance = SheetsAsync(
            spreadsheet_id = config.google.onboarding_id,
            sa_json_path = config.google.service_account_json
        )

    read_res = await _main_sheets_instance.read(rng)

    cols_num: int = len(read_res.get("values")[0])
    res = [el + [""]* (cols_num - len(el)) for el in read_res.get("values")[2:]]

    return res


async def get_students(config: Config) -> list[Student]:
    """
    Get list of students from Google Sheets.
    """
    res: list[list[str]] = await get_main_sheets_instance(config, f"{config.google.student_vitrina_tab}!A1:P")

    students: list[Student] = [
        Student(
            id=col[0], name=col[1], username=col[2], 
            slogan=col[7], prof_experience=col[8], 
            about=col[9], tags=col[11], expectations=col[14],
            telegraph_page=col[15], row=ind+3)
        for ind, col in enumerate(res)]

    return sorted(students, key=lambda x: x.name.split()[1])


async def get_teachers(config: Config) -> list[Teacher]:
    """
    Get list of teachers from Google Sheets.
    """
    res: list[list[str]] = await get_main_sheets_instance(config, f"{config.google.teacher_vitrina_tab}!A1:K")

    teachers: list[Teacher] = [
        Teacher(
            id=col[0], name=col[1], username=col[2],
            about=col[4], prof_experience=col[5],
            tags=col[6], mission=col[7], slogan=col[8],
            telegraph_page=col[10], row=ind+3)
        for ind, col in enumerate(res) if len(col) > 3]

    return sorted(teachers, key=lambda x: x.name.split()[1])


# # Teachers spreadsheet operations
# async def get_teachers(config: Config) -> list[Teacher]:
#     """
#     Get list of teachers from Google Sheets.
#     """
#     sheet: SheetsAsync = get_teachers_sheets_instance(config)

#     read_res = await sheet.read(f"{config.google.accesses_tab}!A1:C{config.google.accesses_tab_length}")

#     teachers: list[Teacher] = [
#         Teacher(id=col[1], name=col[0], disciplines=col[2].split(", ")) 
#         for col in read_res.get("values")[1:] if len(col) > 2]

#     return teachers


# async def get_teachers_ids(config: Config) -> set[int]:
#     """
#     Get list of teachers from Google Sheets.
#     """

#     teachers = await get_teachers(config)

#     return set([teacher.id for teacher in teachers])



async def update_student_name(
        config: Config,
        user_id: int,
        new_name: str):
    """
    Update student name in cell A1 of the user's sheet.
    This is now using the universal update function.
    """
    await update_cell_by_coordinates(
        config=config,
        sheet_name=str(user_id),
        column=1,  # Column A
        row=1,     # Row 1
        value=new_name
    )


def column_number_to_letter(column_number: int) -> str:
    """
    Convert column number to Excel-style column letter.
    
    Args:
        column_number: Column number (1-based, where 1 = A, 2 = B, etc.)
    
    Returns:
        Column letter(s) (e.g., 1 -> 'A', 26 -> 'Z', 27 -> 'AA')
    
    Examples:
        column_number_to_letter(1)   # Returns 'A'
        column_number_to_letter(26)  # Returns 'Z'
        column_number_to_letter(27)  # Returns 'AA'
        column_number_to_letter(702) # Returns 'ZZ'
    """
    if column_number < 1:
        raise ValueError("Column number must be 1 or greater")
    
    result = ""
    while column_number > 0:
        column_number -= 1  # Convert to 0-based
        result = chr(65 + (column_number % 26)) + result
        column_number //= 26
    
    return result


async def update_cell_by_coordinates(
        config: Config,
        sheet_name: str,
        column: int,
        row: int,
        value: str | int | float | None):
    """
    Universal function to update any cell by column and row coordinates.
    
    Args:
        config: Configuration object
        sheet_name: Name of the sheet (e.g., user_id, "Sheet1", etc.)
        column: Column number (1-based, where 1 = A, 2 = B, etc.)
        row: Row number (1-based)
        value: Value to set in the cell
    
    Examples:
        # Update cell A1 (column 1, row 1)
        await update_cell_by_coordinates(config, "123456789", 1, 1, "Hello")
        
        # Update cell B5 (column 2, row 5)
        await update_cell_by_coordinates(config, "123456789", 2, 5, "World")
        
        # Update cell Z10 (column 26, row 10)
        await update_cell_by_coordinates(config, "123456789", 26, 10, 42)
        
        # Update cell AA1 (column 27, row 1)
        await update_cell_by_coordinates(config, "123456789", 27, 1, 3.14)
    """
    sheet: SheetsAsync = get_main_sheets_instance(config)
    
    # Convert column number to letter
    column_letter = column_number_to_letter(column)
    
    # Create cell range (e.g., "A1", "B5", "AA10")
    cell_range = f"{sheet_name}!{column_letter}{row}"
    
    # Update the cell
    await sheet.update(cell_range, [[value]])


async def update_cell_by_letter(
        config: Config,
        sheet_name: str,
        column_letter: str,
        row: int,
        value: str | int | float | None):
    """
    Alternative function to update cell using column letter directly.
    
    Args:
        config: Configuration object
        sheet_name: Name of the sheet
        column_letter: Column letter(s) (e.g., "A", "B", "AA", "ZZ")
        row: Row number (1-based)
        value: Value to set in the cell
    
    Examples:
        # Update cell A1
        await update_cell_by_letter(config, "123456789", "A", 1, "Hello")
        
        # Update cell B5
        await update_cell_by_letter(config, "123456789", "B", 5, "World")
        
        # Update cell AA10
        await update_cell_by_letter(config, "123456789", "AA", 10, 42)
    """
    sheet: SheetsAsync = get_main_sheets_instance(config)
    
    # Create cell range
    cell_range = f"{sheet_name}!{column_letter}{row}"
    
    # Update the cell
    await sheet.update(cell_range, [[value]])