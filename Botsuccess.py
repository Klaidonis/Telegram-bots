import asyncio
import logging
import sys, os
import pandas as pd
import Config as cf # нет
import Otherdoc as Td # нет
import markup as mk2 # нет
import Payment_yookassa # нет
import psycopg2
from yookassa import Configuration, Payment
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

Admins = Td.Admins

api_token = cf.bot_token
pay_token = cf.pay_token

logging.basicConfig(level=logging.INFO)
bot = Bot(token=api_token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
loop = asyncio.get_event_loop()

scheduler = AsyncIOScheduler()
schedulerbg = BackgroundScheduler()

try:
    connect = psycopg2.connect(user="*", password="*", host="*", port="*", database="*")
    cursor = connect.cursor()
    print("Успех подключения")
except:
    print("Провал покдлючения")

try:
    cursor.execute("""CREATE TABLE IF NOT EXISTS people (
    Id BIGINT Primary KEY,
    User_name TEXT,
    Relations INTEGER,
    Status TEXT,
    Beg_date TEXT,
    End_date TEXT,
    Reminder INTEGER,
    End_Reminder INTEGER,
    Reason TEXT,
    Payment_id TEXT,
    Email TEXT,
    Payment_method_id TEXT,
    Autopayment TEXT,
    User_admin INTEGER,
    Date_Reminder TEXT,
    One_Reminder INTEGER
    )""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS price (Id INTEGER, Price INTEGER)""")
    connect.commit()
    print("Успех создания таблицы")
except:
    print("Провал, такая таблица уже создана")

Configuration.secret_key="*"
Configuration.account_id=*

#Только при первом запкуске бота, дальше ее закоментировать

# try:
#     cursor.execute("INSERT INTO price (Id, Price) VALUES (%s, %s);", (2, 1500))
#     connect.commit()
# except:
#     print("В таблицу price уже записаны данные")

class Form(StatesGroup):
    change_admins = State()
    About = State()
    Tariffs = State()
    Delete_id = State()
    Reason_kick = State()
    Un_ban_id = State()
    One_month_amount = State()
    Three_month_amount = State()
    Pinned_message = State()
    Mailing = State()
    End_date = State()
    Reminder_date = State()

class pay_invoice(StatesGroup):
    Email_address = State()

class Date_people(StatesGroup):
    Full_name = State()

@dp.message_handler(commands=['Admin'])
async def admin(message: types.Message):
    if message.from_user.id in Admins and message.text == "/Admin":
        markup = types.ReplyKeyboardMarkup()
        button0 = types.KeyboardButton("Список активных подписчиков")
        button1 = types.KeyboardButton("Список всех подписчиков")
        button2 = types.KeyboardButton("Изменить текст в About")
        button3 = types.KeyboardButton("Изменить текст в subscription")
        button4 = types.KeyboardButton("Разблокировать подписчика")
        button5 = types.KeyboardButton("Удалить подпичика")
        button6 = types.KeyboardButton("Заменить Админа")
        button7 = types.KeyboardButton("Изменить закрепленное сообщение")
        #button7 = types.KeyboardButton("Изменить цену за 1 месяц подписки")
        button8 = types.KeyboardButton("Изменить цену за 3 месяца подписки")
        button9 = types.KeyboardButton("Рассылка всем")
        button10 = types.KeyboardButton("Изменить дату окончания")
        markup.add(button0, button1, button2, button3, button4, button5, button6, button7, button8, button9, button10)
        await message.reply("Админ панель", reply_markup=markup)
        cursor.execute(f"UPDATE people SET User_admin = 1 WHERE Id = {message.from_user.id}")
        connect.commit()

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    pinned_message = await bot.send_message(message.from_user.id, f"{open('Texts/Pinned_message.txt', encoding='UTF-8').read()}")
    await bot.pin_chat_message(chat_id=message.chat.id, message_id = pinned_message.message_id)
    await bot.send_message(message.chat.id, f"{open('Texts/Start.txt', encoding='UTF-8').read()}")
    await message.answer("Укажите вашу почту")
    await pay_invoice.Email_address.set()

@dp.message_handler(commands=['about'])
async def about(message: types.Message):
    About = open("Texts/About.txt", encoding="UTF-8")
    cursor.execute(f"SELECT * FROM people WHERE Id = {message.from_user.id}")
    result = cursor.fetchall()
    for row in result:
        if row[4] == "Failed":
            await bot.send_message(message.from_user.id, "Вы не можете оплатить подписку на канал так как были заблокированы администратором")
        else:
            await bot.send_message(message.from_user.id, About.read())
        connect.commit()

@dp.message_handler(commands=['info'])
async def info(message: types.Message):
    Subscribe = f'SELECT * FROM people WHERE Id = {message.from_user.id}'
    cursor.execute(Subscribe)
    result = cursor.fetchall()
    for row in result:
        await bot.send_message(message.from_user.id, f"Дата оплата подписки: {row[4]}\nДата конца подписки: {row[5]}\nСумма подписки: {row[2]}\nСтатус подписки: {row[3]}")
        connect.commit()

@dp.message_handler(commands=['subscription'])
async def subscription(message: types.Message):
    if message.from_user.id in Admins and message.text == '/subscription':
        await bot.send_message(message.from_user.id, "Вы являетесь админом данного канала, поэтому вы не можете оформлять подписку на канал")
    else:
        cursor.execute(f"SELECT * FROM people WHERE Id = {message.from_user.id}")
        result = cursor.fetchall()
        for row in result:
            if row[4] == "Failed":
                await bot.send_message(message.from_user.id, "Вы не можете оплатить подписку на канал так как были заблокированы администратором")
            else:
                file = open('Texts/Tariffs.txt', encoding='UTF-8')
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                #button0 = types.KeyboardButton("Подписка: 1 месяц")
                button1 = types.KeyboardButton("Подписка: 3 месяца")
                # button2 = types.KeyboardButton("Автоплатеж: ДА")
                # button3 = types.KeyboardButton("Автоплатеж: НЕТ")
                button4 = types.KeyboardButton("Отменить подписку")
                markup.add(button1, button4)
                await message.answer(file.read())
                await message.answer("Здесь вы можете управлять своей подпиской", reply_markup=markup)
            connect.commit()

@dp.message_handler(commands=['Excel'])
async def upload_to_excel(message: types.Message):
    if message.from_user.id in Admins and message.text == "/Excel":
        try:
            path = 'C:/Excel from tg'
            os.mkdir(path)
        except FileExistsError:
            print("Папка уже создана")
        date = datetime.now().date()
        People = pd.read_sql('select * from people', connect)
        People.to_excel(fr'C:/Excel from tg/People {date}.xlsx', index=False)
        await bot.send_message(message.from_user.id, "Excel файл создан\nПуть к нему: C:/Excel from tg/")
    else:
        await bot.send_message(message.from_user.id, "У вас нет прав для этой команды")

@dp.message_handler(commands=['support'])
async def support(message: types.Message):
    Admin_user = open('Texts/Admins.txt', 'r', encoding='UTF-8')
    await bot.send_message(message.from_user.id, f"По всем вопросам пишите: {Admin_user.read()}")

@dp.message_handler(content_types=['text'])
async def admin_panel(message: types.Message):
    if message.from_user.id in Admins and message.text == "Список активных подписчиков":
        List_people = f"SELECT * FROM people WHERE Status = 'success' "
        cursor.execute(List_people)
        result = cursor.fetchall()
        await bot.send_message(message.from_user.id, f"Кол-во всех подписчиков: {len(result)}")
        for row in result:
            await bot.send_message(message.chat.id,f"Id: {row[0]}\nИмя: {row[1]}\nПочта: {row[10]}\nСумма оплаты: {row[2]}\nСтатус подписки: {row[3]}\nДата оплаты подписки: {row[4]}\nКонец подписки: {row[5]}")
            connect.commit()
    elif message.from_user.id in Admins and message.text == "Список всех подписчиков":
        List_people = f"SELECT * FROM people"
        cursor.execute(List_people)
        result = cursor.fetchall()
        await bot.send_message(message.from_user.id, f"Кол-во всех подписчиков: {len(result)}")
        for row in result:
            await bot.send_message(message.chat.id, f"Id: {row[0]}\nИмя: {row[1]}\nПочта: {row[10]}\nСумма оплаты: {row[2]}\nСтатус подписки: {row[3]}\nДата оплаты подписки: {row[4]}\nКонец подписки: {row[5]}")
            connect.commit()
    elif message.from_user.id in Admins and message.text == "Изменить текст в About":
        await message.answer("Напишите текст")
        await Form.About.set()
    elif message.from_user.id in Admins and message.text == "Изменить текст в subscription":
        await message.answer("Напишите текст")
        await Form.Tariffs.set()
    elif message.from_user.id in Admins and message.text == "Разблокировать подписчика":
        await message.answer("Укажите Id для разблокировки")
        await Form.Un_ban_id.set()
    elif message.from_user.id in Admins and message.text == "Удалить подпичика":
        await message.answer("Напишите Id пользователя которого хотите кикнуть")
        await Form.Delete_id.set()
    # elif message.from_user.id in Admins and message.text == "Изменить цену за 1 месяц подписки":
    #     await message.answer("Укажите цену за 1 месяц подписки")
    #     await Form.One_month_amount.set()
    elif message.from_user.id in Admins and message.text == "Изменить цену за 3 месяца подписки":
        await message.answer("Укажите цену за 3 месяцa подписки")
        await Form.Three_month_amount.set()
    elif message.from_user.id in Admins and message.text == "Заменить Админа":
        await message.answer("Напишите ник Админа")
        await Form.change_admins.set()
    elif message.from_user.id in Admins and message.text == "Изменить закрепленное сообщение":
        await message.answer("Напишите новое сообщение")
        await Form.Pinned_message.set()
    elif message.from_user.id in Admins and message.text == "Рассылка всем":
        await message.answer("Какое сообщение разослать всем?")
        await Form.Mailing.set()
    elif message.from_user.id in Admins and message.text == "Изменить дату окончания":
        await bot.send_message(message.from_user.id, "Дата должна быть указана строго в следующем порядке\nГОД-МЕСЯЦ-ДЕНЬ ЧАС-МИНУТА\n2020-06-18 13-00")
        await Form.End_date.set()
    # elif message.text == "Подписка: 1 месяц":
    #     link, payment = Payment_yookassa.create_one_month_invoice(message)
    #     await bot.send_message(message.from_user.id, 'Подписка: 1 Месяц', reply_markup=mk.markup_pay(link, payment))
    elif message.text == "Подписка: 3 месяца":
        link, payment = Payment_yookassa.create_three_month_invoice(message)
        await message.answer('Подписка: 3 Месяца', reply_markup=mk2.markup_pay2(link, payment))
    elif message.text == "Отменить подписку":
        # cursor.execute(f"UPDATE people SET Status = 'cancel' WHERE Id = {message.from_user.id}")
        cursor.execute(f"UPDATE people SET Autopayment = 'false' WHERE Id = {message.from_user.id}")
        await message.answer("Вы отменили подписку на следующий сезон")
        connect.commit()

@dp.message_handler(state=Form.About)
async def get_about(message: types.Message, state: FSMContext):
    await state.update_data(about = message.text)
    data = await state.get_data()
    about = data['about']
    file = open('Texts/About.txt', 'w', encoding="UTF-8")
    file.write(f'{about}')
    file.close()
    await state.finish()

@dp.message_handler(state=Form.Tariffs)
async def get_about(message: types.Message, state: FSMContext):
    await state.update_data(tariffs = message.text)
    data = await state.get_data()
    tariffs = data['tariffs']
    file = open('Texts/Tariffs.txt', 'w', encoding="UTF-8")
    file.write(f'{tariffs}')
    file.close()
    await state.finish()

@dp.message_handler(state=Form.Delete_id)
async def delete_user_id(message: types.Message, state: FSMContext):
    await state.update_data(delete_user_id = message.text)
    await message.answer("Укажите причину изгнания")
    await Form.next()

@dp.message_handler(state=Form.Reason_kick)
async def get_about(message: types.Message, state: FSMContext):
    await state.update_data(Reason_kick = message.text)
    data = await state.get_data()
    delete_user_id = data['delete_user_id']
    reason_kick =  data['Reason_kick']
    await bot.kick_chat_member(user_id=delete_user_id, chat_id=(-1001988589258))
    cursor.execute(f"UPDATE people SET Reason = '{reason_kick}' WHERE Id = {delete_user_id}")
    cursor.execute(f"UPDATE people SET Status = 'Failed' WHERE Id = {delete_user_id}")
    cursor.execute(f'SELECT * FROM people WHERE Id = {delete_user_id}')
    result = cursor.fetchall()
    for row in result:
        await bot.send_message(message.from_user.id, f"Удален из канала\nИмя: {row[1]}\nНик телеграмма: {row[2]}\nПричина: {row[9]}")
        await bot.send_message(delete_user_id, f"Вы удалены из каналы по желанию админа\nПричина: {row[9]}")
        connect.commit()
    await state.finish()
    connect.commit()

@dp.message_handler(state=Form.Un_ban_id)
async def un_bun_id(message: types.Message, state: FSMContext):
    await state.update_data(un_bun_id = message.text)
    data = await state.get_data()
    un_bun_id = data['un_bun_id']
    await bot.unban_chat_member(user_id=un_bun_id, chat_id=(-1001988589258))
    await bot.send_message(un_bun_id, "Вы были разблокированы администратором")
    cursor.execute(f"UPDATE people SET Status = '' WHERE Id = {un_bun_id}")
    cursor.execute(f"UPDATE people SET Beg_date = '' WHERE Id = {un_bun_id}")
    cursor.execute(f"UPDATE people SET End_date = '' WHERE Id = {un_bun_id}")
    cursor.execute(f"UPDATE people SET Reason = '' WHERE Id = {un_bun_id}")
    connect.commit()
    await state.finish()

@dp.message_handler(state=Form.change_admins)
async def change_admins(message: types.Message, state: FSMContext):
    await state.update_data(change_admins = message.text)
    data = await state.get_data()
    change_admins = data['change_admins']
    file = open('Texts/Admins.txt', 'w', encoding='UTF-8')
    file.write(f"{change_admins}")
    file.close()
    await message.reply("Вы изменили админа отвечающего на вопросы")
    await state.finish()

# @dp.message_handler(state=Form.One_month_amount)
# async def change_price_one_month(message: types.Message, state: FSMContext):
#     await state.update_data(change_price_one_month = message.text)
#     data = await state.get_data()
#     change_price_one_month = data['change_price_one_month']
#     cursor.execute(f"UPDATE price SET Price = {change_price_one_month} WHERE Id = 1")
#     await message.reply(f"Вы изменили цену за 1 месяц на: {change_price_one_month}")
#     await state.finish()
#     connect.commit()

@dp.message_handler(state=Form.Three_month_amount)
async def change_price_three_month(message: types.Message, state: FSMContext):
    await state.update_data(change_price_three_month = message.text)
    data = await state.get_data()
    change_price_three_month = data['change_price_three_month']
    cursor.execute(f"UPDATE price SET Price = {change_price_three_month} WHERE Id = 2")
    await message.reply(f"Вы изменили цену за 1 месяц на: {change_price_three_month}")
    await state.finish()
    connect.commit()

@dp.message_handler(state=Form.Pinned_message)
async def Pinned_message(message: types.Message, state: FSMContext):
    cursor.execute(f"SELECT * FROM people")
    for row in cursor.fetchall():
        await state.update_data(Pinned_message = message.text)
        data = await state.get_data()
        Pinned_message = data['Pinned_message']
        file = open('Texts/Pinned_message.txt', 'w', encoding='UTF-8')
        file.write(f"{Pinned_message}")
        file.close()
        pinned_message = await bot.send_message(row[0], open('Texts/Pinned_message.txt', encoding='UTF-8').read())
        await bot.pin_chat_message(chat_id=row[0], message_id=pinned_message.message_id)
        await state.finish()
        connect.commit()

@dp.message_handler(state=Form.Mailing)
async def mailing_all(message: types.Message, state: FSMContext):
    await state.update_data(mailing_all = message.text)
    data = await state.get_data()
    mailing_all = data['mailing_all']
    cursor.execute("SELECT * FROM people")
    for row in cursor.fetchall():
        await bot.send_message(row[0], mailing_all)
    connect.commit()
    await state.finish()

@dp.message_handler(state=Form.End_date)
async def end_date(message: types.Message, state: FSMContext):
    await state.update_data(end_date = message.text)
    await message.answer("Укажите дату уведомления об окончании подписки в таком же формате")
    await Form.next()

@dp.message_handler(state=Form.Reminder_date)
async def Reminder_date(message: types.Message, state: FSMContext):
    await state.update_data(Reminder_date = message.text)
    data = await state.get_data()
    end_date = data['end_date']
    Reminder_date = data['Reminder_date']
    file = open('Texts/End_date.txt', 'w', encoding='UTF-8')
    file.write(f"{end_date}")
    file.close()
    file2 = open('Texts/Reminder_date.txt', 'w', encoding='UTF-8')
    file2.write(f"{Reminder_date}")
    file2.close()
    await message.answer(f"Вы изменили дату уведомления: {open('Texts/Reminder_date.txt', encoding='UTF-8').read()}")
    await message.answer(f"Вы изменили окончание подписки: {open('Texts/End_date.txt', encoding='UTF-8').read()}")
    await state.finish()

@dp.message_handler(state=pay_invoice.Email_address)
async def get_email_address(message: types.Message, state: FSMContext):
    await state.update_data(get_email_address = message.text)
    data = await state.get_data()
    Email = data['get_email_address']
    Check_email1 = "gmail.com"
    Check_email2 = "yandex.ru"
    Check_email3 = "mail.ru"
    Check_email4 = "yoahoo.com"
    if Email.__contains__(Check_email1) or Email.__contains__(Check_email2) or Email.__contains__(Check_email3) or Email.__contains__(Check_email4):
        if message.from_user.id in Admins:
            try:
                Id = message.from_user.id
                User_name = message.from_user.first_name
                Relations = 0
                Status = ""
                Beg_date = ""
                End_date = ""
                Reminder = 0
                End_Reminder = 0
                Reason = ""
                Payment_id = ""
                Payment_method_id = ""
                Autopayment = ""
                User_admin = 1
                Date_reminder = ""
                One_Reminder = 0
                cursor.execute("INSERT INTO people (Id, User_name, Relations, Status, Beg_date, End_date, Reminder, End_Reminder, Reason, Payment_id, Email, Payment_method_id, Autopayment, User_admin, Date_Reminder, One_Reminder) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);", (Id, User_name, Relations, Status, Beg_date, End_date, Reminder, End_Reminder, Reason, Payment_id, Email, Payment_method_id, Autopayment, User_admin, Date_reminder, One_Reminder))
                await bot.send_message(message.from_user.id, "Вы успешно зарегистрировались")
            except:
                await bot.send_message(message.from_user.id, "Вы уже зарегестрированы")
                connect.commit()
        elif message.from_user.id not in Admins:
            try:
                Id = message.from_user.id
                User_name = message.from_user.first_name
                Relations = 0
                Status = ""
                Beg_date = ""
                End_date = ""
                Reminder = 0
                End_Reminder = 0
                Reason = ""
                Payment_id = ""
                Payment_method_id = ""
                Autopayment = ""
                User_admin = 0
                Date_reminder = ""
                One_Reminder = 0
                cursor.execute("INSERT INTO people (Id, User_name, Relations, Status, Beg_date, End_date, Reminder, End_Reminder, Reason, Payment_id, Email, Payment_method_id, Autopayment, User_admin, Date_Reminder, One_Reminder) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);", (Id, User_name, Relations, Status, Beg_date, End_date, Reminder, End_Reminder, Reason, Payment_id, Email, Payment_method_id, Autopayment, User_admin, Date_reminder, One_Reminder))
                await bot.send_message(message.from_user.id, "Вы успешно зарегистрировались")
            except:
                await bot.send_message(message.from_user.id, "Вы уже зарегестрированы")
            connect.commit()
        await state.finish()
    else:
        await bot.send_message(message.from_user.id, "Почта введена не корректно, попробуйте еще раз")
@dp.callback_query_handler()
async def check_one_month(call: types.CallbackQuery):
    if call.message['text'] == "Подписка: 3 Месяца" or "/tariffs" or "/about":
        check = Payment_yookassa.check_three_month(call.data, call.message)
        if check:
            chat_id_unban = (-1001988589258)
            expire_date = datetime.now() + timedelta(days=1)
            link = await bot.create_chat_invite_link(chat_id_unban, expire_date.timestamp, 1)
            await bot.unban_chat_member(user_id=call.from_user.id, chat_id=chat_id_unban)
            await bot.send_message(chat_id=call.from_user.id, text="Оплачено")
            await bot.send_message(call.from_user.id, "Вы получили ссылку на одно вхождение")
            await bot.send_message(call.from_user.id, link.invite_link)
        else:
            await bot.send_message(chat_id=call.from_user.id, text=f"Оплата не прошла\nОбратитесь к Админу для выяснения обстоятельств: {open('Texts/Admins.txt', encoding='UTF-8').read()}")


#Изменения на 22.08.2023
async def reminder_for_the_day():
    cursor.execute(f"SELECT * FROM people WHERE User_admin = 0 and Reminder = 0 and Status = 'success'")
    result = cursor.fetchall()
    for row in result:
        if str(datetime.now()) >= str(row[14]):
            await bot.send_message(row[0], "Завтра у вас закончится подписка\nоплатите чтобы не потерять доступ к каналу")
            cursor.execute(f"UPDATE people SET Reminder = 1")
            connect.commit()

async def ban_member_cancel():
    cursor.execute(f"SELECT * FROM people WHERE User_admin = 0 and End_Reminder = 0 and Status = 'success'")
    result = cursor.fetchall()
    for row in result:
        if str(datetime.now()) >= str(row[5]):
            await bot.ban_chat_member(user_id=row[0], chat_id=(-1001988589258))
            await bot.send_message(row[0], "Вы забыли оплатить подписку на канал, поэтому вы будете исключены, на период пока подписка не будет оплачена")
            cursor.execute(f"UPDATE people SET Status = 'cancel'")
            cursor.execute(f"UPDATE people SET Reason = 'Не оплатил подписку'")
            cursor.execute(f"UPDATE people SET End_Reminder = 1")
            connect.commit()

async def create_autopayment():
    cursor.execute("SELECT * FROM people WHERE Autopayment = 'true' and One_reminder = 0")
    result = cursor.fetchall()
    for row in result:
        cursor.execute("SELECT * FROM price WHERE Id = 2")
        for row2 in cursor.fetchall():
            if str(datetime.now()) >= str(row[5]):
                payment = Payment.create({
                    "amount": {
                        "value": row2[1],
                        "currency": "RUB"
                    },
                    "capture": True,
                    "payment_method_id": f"{row[11]}",
                    "receipt": {
                        "customer": {
                        "full_name": f"{row[1]}",
                        'email': f'{row[10]}'
                    },
                        "items": [
                            {
                            "description": "Подписка на канала",
                            "quantity": "1.00",
                            "amount": {
                                "value": row2[1],
                                "currency": "RUB"
                            },
                            "payment_method_data":  {
                                "type": "bank_card"
                            },
                            "vat_code": "2",
                                "payment_mode": "full_prepayment",
                                "payment_subject": "commodity"
                        }
                        ]
                    }
                })
                if payment.status == "succeeded":
                    await bot.send_message(row[0], "Ваша подписка продлена")
                    Beg_date = (datetime.now().strftime('%Y-%m-%d %H-%M'))
                    Three_month = open('Texts/End_date.txt', encoding='UTF-8').read()
                    Reminder_date = open('Texts/Reminder_date.txt', encoding='UTF-8').read()
                    cursor.execute(f"UPDATE people SET Status = 'success' WHERE Payment_method_id = '{payment.payment_method.id}'")
                    cursor.execute(f"UPDATE people SET Beg_date = '{Beg_date}' WHERE Payment_method_id  = '{payment.payment_method.id}'")
                    cursor.execute(f"UPDATE people SET End_date = '{Three_month}' WHERE Payment_method_id  = '{payment.payment_method.id}'")
                    cursor.execute(f"UPDATE people SET Reminder = 0 WHERE Payment_method_id  = '{payment.payment_method.id}'")
                    cursor.execute(f"UPDATE people SET End_Reminder = 0 WHERE Payment_method_id  = '{payment.payment_method.id}'")
                    cursor.execute(f"UPDATE people SET Reason = '' WHERE Payment_method_id  = '{payment.payment_method.id}'")
                    cursor.execute(f"UPDATE people SET Date_Reminder = '{Reminder_date}' WHERE Payment_method_id  = '{payment.payment_method.id}'")
                    cursor.execute(f"UPDATE people SET One_Reminder = 1 WHERE Payment_method_id  = '{payment.payment_method.id}'")
                    connect.commit()
                elif payment.status == "canceled":
                    await asyncio.sleep(3)
                    await bot.send_message(row[0], "Не удалось продлить подписку, проверьте ваш баланс на карте и пополните вручную")
                    cursor.execute(f"UPDATE people SET One_reminder = 1 WHERE Payment_method_id = '{payment.payment_method.id}'")
                    connect.commit()


if __name__ == "__main__":
    scheduler.add_job(ban_member_cancel, 'interval', seconds=3600)
    scheduler.add_job(reminder_for_the_day, 'interval', seconds=3600)
    scheduler.add_job(create_autopayment, 'interval', seconds=1800)
    scheduler.start()
    executor.start_polling(dp, skip_updates=True)
