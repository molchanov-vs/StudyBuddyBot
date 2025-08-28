# StudyBuddyBot


## installation
```bash
chmod +x setup.sh
./setup.sh
```





## Todo
- [x] Bold and other HTML formatting
- [x] add chat after offboarding - похоже не нужно
- [x] Уберу необходимость нажатия на старт при перезапуске бота
- [x] Буду ориентироваться что завтра запускаемся: завтра онбординг, а после завтра первый пуш
- [ ] По образу и подобию сделаю Виктора.
- [x] Нотификация мне если не будет работать чат
- [x] Статистика для админов по входам
- [x] Кнопка back
- [ ] Разметить данные для Тани


## Redis Insight
```bash
# SSH tunnel for Redis connection
ssh -L 6379:127.0.0.1:6379 a2816@192.168.0.13

# Then connect Redis Insight to: localhost:6379
```

## Useful
Про bg https://t.me/aiogram_dialog/150388

https://github.com/Tishka17/aiogram_dialog/issues/263

```python
@router.message(Command('send_notification'),
                StateFilter(UserState.REGISTERED))
async def notify_handler(update: Message, bot: Bot,
                         dialog_bg_factory: BgManagerFactory,
                         session_maker_db: Session) -> None:
    '''Отправляет уведомление о приеме с клавиатурой для взаимодействия с
    приемом.

    Flow:
        1. Получает данные из хранилища Redis
        2. Удаляет все запланированные задачи
        3. Отправляет сообщение с уведомлением о приеме
        4. Добавляет id сообщения в хранилище Redis
        5. Запускает задачи на отправку уведомлений о недозвоне и удаление
        клавиатуры из первого сообщения при отправке последнего уведомления о
        недозвоне
        6. Устанавливает новое состояние
    '''

    receptions = await DataBaseService.get_receptions_by_date(session_maker_db)
    for reception, username_id in receptions:
        prepared_notification_msg = await DataService.prepare_notification_msg(
            session_maker_db, reception)
        data = await DataBaseService.get_data_for_msg(session_maker_db, reception)
        bg_manager: BgManager = dialog_bg_factory.bg(bot=bot,
                                                     user_id=username_id,
                                                     chat_id=username_id)
        await bg_manager.start(state=MainDialog.MAIN_MENU,
                               mode=StartMode.RESET_STACK,
                               data={'prepared_notification_msg':
                                     prepared_notification_msg,
                                     'data': data})
```


## Done
- Подключил чат к аккаунту Насти Брудковой
- Надпись typing во время генерирования ответа ботом
- Пользователь не сможет начать беседу с чатом пока не пройдёт онбординг


## dump
```python
for user in users:

    if user in admins:
        continue

    user_data_raw = users_storage.lrange(f"{user}", 0, -1)

    if not os.path.isdir(f"./dump/{user}"):
        os.makedirs(f"./dump/{user}")

    # user_data
    user_datag_raw = users_storage.lrange(f"{user}", 0, -1)
    user_data = [UserData.model_validate_json(u).model_dump() for u in user_datag_raw]
    with open(f"./dump/{user}/user.json", 'w', encoding="utf-8") as f:
        json.dump(user_data[:1], f, indent=4, ensure_ascii=False)

    # onboarding
    onboarding_raw = users_storage.lrange(f"{user}_on", 0, -1)
    onboarding = [UserOnboarding.model_validate_json(on).model_dump() for on in onboarding_raw]
    with open(f"./dump/{user}/onboarding.json", 'w', encoding="utf-8") as f:
        json.dump(onboarding[:1], f, indent=4, ensure_ascii=False)

    # history
    history_raw = users_storage.lrange(f"{user}_h", 0, -1)
    history = [MessageForGPT.model_validate_json(h).model_dump() for h in history_raw]
    with open(f"./dump/{user}/history.json", 'w', encoding="utf-8") as f:
        json.dump(history, f, indent=4, ensure_ascii=False)

```