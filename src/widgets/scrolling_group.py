from typing import Dict, List, Union, Optional

from aiogram.types import InlineKeyboardButton, CallbackQuery

from aiogram_dialog.api.internal import RawKeyboard
from aiogram_dialog.api.protocols import DialogManager
from aiogram_dialog.api.protocols import DialogProtocol

from aiogram_dialog.widgets.kbd import ScrollingGroup
from aiogram_dialog.widgets.common import OnPageChangedVariants, WhenCondition


class CustomScrollingGroup(ScrollingGroup):

    def __init__(
            self,
            *buttons,
            id: str,
            width: Optional[int] = None,
            height: int = 0,
            when: WhenCondition = None,
            on_page_changed: OnPageChangedVariants = None,
            hide_on_single_page: bool = False,
            hide_pager: bool = False,
            back_btn: str = "<",
            forward_btn: str = ">",
            back_btn_text: str = "Назад",
    ):
        super().__init__(
            *buttons,
            id=id,
            width=width,
            height=height,
            when=when,
            on_page_changed=on_page_changed,
            hide_on_single_page=hide_on_single_page,
            hide_pager=hide_pager,
        )
        self.back_btn = back_btn
        self.forward_btn = forward_btn
        self.back_btn_text = back_btn_text


    async def _render_pager(
            self,
            pages: int,
            manager: DialogManager,
    ) -> RawKeyboard:
        if self.hide_pager:
            return []
        if pages == 0 or (pages == 1 and self.hide_on_single_page):
            return []

        last_page = pages - 1
        current_page = min(last_page, await self.get_page(manager))
        next_page = min(last_page, current_page + 1)
        prev_page = max(0, current_page - 1)

        return [
            [
                InlineKeyboardButton(
                    text=self.back_btn,
                    callback_data=self._item_callback_data(prev_page),
                ),
                InlineKeyboardButton(
                    text=self.back_btn_text,
                    callback_data=self._item_callback_data("back"),
                ),
                InlineKeyboardButton(
                    text=self.forward_btn,
                    callback_data=self._item_callback_data(next_page),
                )
            ],
        ]


    async def _process_item_callback(
            self,
            callback: CallbackQuery,
            data: str,
            dialog: DialogProtocol,
            manager: DialogManager,
    ) -> bool:

        if data == "back":
            await manager.done()
            return True

        await self.set_page(callback, int(data), manager)
        return True