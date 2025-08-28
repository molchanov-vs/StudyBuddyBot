import os

from logging import basicConfig, Formatter, getLogger, \
    WARNING, INFO

from datetime import datetime
import pytz

from my_tools import get_datetime_now


def start_logging(time_zone):

    if not os.path.exists('logs'):
        os.makedirs('logs')

    file_name = get_datetime_now()
    path_to_log_file = f'logs/{file_name}.log'
        
    tz = pytz.timezone(time_zone)
    Formatter.converter = lambda *args: datetime.now(tz=tz).timetuple()
    basicConfig(
        filename=path_to_log_file,
        level=INFO, # WARNING
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    logger = getLogger(__name__)
    logger.warning("Bot has just started..!")