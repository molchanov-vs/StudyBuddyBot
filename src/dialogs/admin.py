import logging
import operator

from datetime import datetime

from aiogram.fsm.storage.redis import RedisStorage
from aiogram_dialog import \
    Dialog, Window, LaunchMode, DialogManager, StartMode, ShowMode
from aiogram_dialog.widgets.kbd import \
    Button, ListGroup, Url, ManagedRadio, Row, Radio, Start
from aiogram_dialog.widgets.text import Format, Const

from ..custom_types import UserData, UserAction

from ..config import Config
from ..states import Admin, Onboarding

from ..utils.pusher import run_pusher, finish_onboarding
from ..utils.utils import get_middleware_data

from my_tools import get_users, Langs, get_time_delta


async def set_radio_default(_, dialog_manager: DialogManager):
    
    item_id = '5'
    radio_num: ManagedRadio = dialog_manager.find("radio_num")
    await radio_num.set_checked(item_id)

    item_status = "new"
    radio_status: ManagedRadio = dialog_manager.find("radio_status")
    await radio_status.set_checked(item_status)


async def get_last_users(
        dialog_manager: DialogManager,
        config: Config, 
        **kwargs) -> list[UserData]:
    
    users: RedisStorage = kwargs.get("users")
    
    num = dialog_manager.find('radio_num').get_checked()
    st = dialog_manager.find('radio_status').get_checked()

    numbers = [
        ("5️⃣", "5"),
        ("🔟", "10")
    ]

    status = [
        ("🐣", "new"),
        ("🎖️", "old")
    ]

    users_id: list[int] = await get_users(users, config.admins.ids + config.superadmins.ids)
    users_id: list[int] = [id for id in users_id if int(id) not in config.superadmins.ids]
    users_data: list[UserData] = []

    for user_id in users_id:

        user_raw_data = await users.redis.lindex(user_id, 0)
        user_data: UserData = UserData.model_validate_json(user_raw_data)
            
        if st == "old":
            user_action_data = await users.redis.lindex(f"{user_id}_a", 0)
            try:
                user_action: UserAction = UserAction.model_validate_json(user_action_data)
                user_data.date = user_action.date
            except:
                logging.warning(f"CHECK redis: {user_action_data}")

        
        users_data.append(user_data)


    # Sort users by the 'date' field (assuming ISO format) in descending order
    users_sorted: list[UserData] = sorted(users_data, key=lambda u: datetime.fromisoformat(u.date), reverse=True)
    

    last_users = [
        {
            "name": f"{Langs.__members__.get(u.language_code, u.language_code).value}{"🌟" if u.is_premium else ""} {u.full_name} {get_time_delta(u.date)}",
            "url": f"{u.username}" if u.username else "https://t.me/unknown",
        } for u in users_sorted[:int(num)]
    ]

    return {
        "last_users": last_users,
        "numbers": numbers,
        "status": status,
        "users": f"👤 Users: {len(users_id)}"
        }

async def dialog_get_data(
        dialog_manager: DialogManager,
        config: Config,
        temp: RedisStorage,
        **kwargs):
    
    _, config, user_data = get_middleware_data(dialog_manager)
    value_counter = await temp.redis.get(f"{config.bot.id}:counter")
    if not value_counter:
        await temp.redis.set(f"{config.bot.id}:counter", 1)
    
    data = {
        "stats": f"📊<b>{config.bot.name}:</b>",
        "value_counter": int(value_counter) if value_counter else 1
    }

    res = await temp.redis.zrange("pusher_job_runner", 0, -1)

    if not res and user_data.id in config.superadmins.ids:
        data["run_pusher"] = True

    data["finish_onboarding"] = True

    return data


dialog = Dialog(
    Window(

        Const("🛠️ Admin Panel 🛠️"),

        Format("{stats}"),
        Const("--------------------"),
        Format("{users}"),

        Button(
            text=Format("🔥 Finish onboarding"),
            id="finish_onboarding_id",
            on_click=finish_onboarding,
            when="finish_onboarding"
        ),
        
        # Button(
        #     text=Format("🔥 Run pusher ({value_counter})"),
        #     id="run_pusher_id",
        #     on_click=run_pusher,
        #     when="run_pusher"
        # ),

        ListGroup(
            Url(
                Format("{item[name]} "),
                Format("{item[url]}"),
                id="url",
            ),
            id="select_last_users",
            item_id_getter=lambda item: item["name"],
            items="last_users",
        ),


        Row(
            Radio(
                checked_text=Format('🔘 {item[0]}'),
                unchecked_text=Format('⚪️ {item[0]}'),
                id='radio_status',
                item_id_getter=operator.itemgetter(1),
                items="status",
            ),
        ),

        Row(
            Radio(
                checked_text=Format('🔘 {item[0]}'),
                unchecked_text=Format('⚪️ {item[0]}'),
                id='radio_num',
                item_id_getter=operator.itemgetter(1),
                items="numbers",
            ),
        ),
        
        Row(
            Start(
                text=Const("🔙"),
                id="back_btn",
                state=Onboarding.WELCOME,
                show_mode=ShowMode.DELETE_AND_SEND,
                mode=StartMode.RESET_STACK
            ),
            
            Button(
                text=Const("🔄 Update"),
                id="update_btn"
            ),
        ),

        state=Admin.MAIN,
        getter=get_last_users
    ),
    launch_mode=LaunchMode.ROOT,
    on_start=set_radio_default,
    getter=dialog_get_data
)