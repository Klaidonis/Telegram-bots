import psycopg2
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

try:
    connect = psycopg2.connect(user="*", password="*", host="*", port="*", database="*")
    cursor = connect.cursor()
    print("Успех")
except:
    print("Провал")

def markup_pay2(url, id):
    cursor.execute(f"SELECT * FROM price WHERE Id = 2")
    result2 = cursor.fetchall()
    for row2 in result2:
        markup = InlineKeyboardMarkup(row_width=1)
        button0 = InlineKeyboardButton(f"Оплатить: {row2[1]} RUB за 3 месяца", url=url)
        button1 = InlineKeyboardButton("Проверить оплату", callback_data=id)
        markup.add(button0, button1)
        return markup
    connect.commit()