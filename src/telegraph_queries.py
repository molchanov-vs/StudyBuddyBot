import logging

from telegraph import Telegraph

from .custom_types import Teacher, Student

from .config import Config



def update_telegraph_page(config: Config, person: dict, role: str):


    if role == "student":
        person = Student(**person)
    else:
        person = Teacher(**person)

    telegraph = Telegraph(access_token=config.telegraph.access_token)

    request = telegraph.edit_page(
        path=person.telegraph_page.split("/")[-1],
        title=person.name,
        author_name=config.bot.name,
        author_url=str(config.bot.link),
        html_content=f"""
            <p><b>📍 О себе</b></p>
            <p>{person.about}</p>
            <br>
            <p><b>💼 Профессиональный опыт</b></p>
            <p>{person.prof_experience}</p>
        """
        )

    logging.info(f"Telegraph page updated for {person.name}")