import asyncio
import psycopg2
from datetime import datetime, timedelta
from yookassa import Configuration, Payment, Receipt
from aiogram import Bot, Dispatcher, executor, types

try:
    connect = psycopg2.connect(user="*", password="*", host="*", port="*", database="*")
    cursor = connect.cursor()
    print("Успех")
except:
    print("Провал")

Configuration.secret_key="*"
Configuration.account_id=*

# def create_one_month_invoice(message: types.Message):
#     cursor.execute(f"SELECT * FROM people WHERE Id = {message.chat.id}")
#     result = cursor.fetchall()
#     cursor.execute(f"SELECT * FROM price WHERE Id = 1")
#     result2 = cursor.fetchall()
#     for row in result:
#         for row2 in result2:
#             payment = Payment.create({
#                 "amount": {
#                     "value": row2[1],
#                     "currency": "RUB"
#                 },
#                 "capture": True,
#                 "confirmation": {
#                     "type": "redirect",
#                     "return_url": "https://www.example.com/return_url"
#                 },
#                 "receipt": {
#                     "customer": {
#                         "full_name": f"{row[1]}",
#                         "email": f"{row[10]}",
#                         "phone": "79000000000"
#                     },
#                     "items": [
#                         {
#                             "description": "Наименование товара 1",
#                             "quantity": "1.00",
#                             "amount": {
#                                 "value": row2[1],
#                                 "currency": "RUB"
#                             },
#                             "vat_code": "2",
#                             "payment_mode": "full_prepayment",
#                             "payment_subject": "commodity"
#                         }
#                     ]
#                 },
#             })
#             url = payment.confirmation.confirmation_url
#             return url, payment.id

def create_three_month_invoice(message: types.Message):
    cursor.execute(f"SELECT * FROM people WHERE Id = {message.chat.id}")
    result = cursor.fetchall()
    cursor.execute(f"SELECT * FROM price WHERE Id = 2")
    result2 = cursor.fetchall()
    for row in result:
        for row2 in result2:
            payment = Payment.create({
                "amount": {
                    "value": row2[1],
                    "currency": "RUB"
                },
                "capture": True,
                "confirmation": {
                    "type": "redirect",
                    "return_url": "https://t.me/Shutova_test_assist_bot"
                },
                "receipt": {
                    "customer": {
                        "full_name": f"{row[1]}",
                        'email': f'{row[10]}'
                    },
                    "items": [
                        {
                            "description": "Подписка на канал",
                            "quantity": "1.00",
                            "amount": {
                                "value": row2[1],
                                "currency": "RUB"
                            },
                            "payment_method_data": {
                                "type": "bank_card" or "sberbank"
                            },
                            "vat_code": "2",
                            "payment_mode": "full_prepayment",
                            "payment_subject": "commodity"
                        }
                    ]
                },
            })
            url = payment.confirmation.confirmation_url
            return url, payment.id

def check_three_month(id, message: types.Message):
    payment = Payment.find_one(id)
    Beg_date = (datetime.now().strftime('%Y-%m-%d %H-%M'))
    Three_month = open('Texts/End_date.txt', encoding='UTF-8').read()
    Reminder_date = open('Texts/Reminder_date.txt', encoding='UTF-8').read()
    if payment.status == "succeeded":
        save_payment = payment.payment_method.saved
        cursor.execute(f"SELECT * FROM people WHERE Id = {message.chat.id}")
        result = cursor.fetchall()
        for row in result:
            cursor.execute(f"SELECT * FROM price WHERE Id = 2")
            result2 = cursor.fetchall()
            for row2 in result2:
                cursor.execute(f"UPDATE people SET Relations = {row2[1]} WHERE Id = {message.chat.id}")
                cursor.execute(f"UPDATE people SET Status = 'success' WHERE Id = {message.chat.id}")
                cursor.execute(f"UPDATE people SET Beg_date = '{Beg_date}' WHERE Id = {message.chat.id}")
                cursor.execute(f"UPDATE people SET End_date = '{Three_month}' WHERE Id = {message.chat.id}")
                cursor.execute(f"UPDATE people SET Reminder = 0 WHERE Id = {message.chat.id}")
                cursor.execute(f"UPDATE people SET End_Reminder = 0 WHERE Id = {message.chat.id}")
                cursor.execute(f"UPDATE people SET Reason = '' WHERE Id = {message.chat.id}")
                cursor.execute(f"UPDATE people SET Payment_id = '{payment.id}' WHERE Id = {message.chat.id}")
                cursor.execute(f"UPDATE people SET Payment_method_id = '{payment.id}' WHERE Id = {message.chat.id}")
                cursor.execute(f"UPDATE people SET Date_Reminder = '{Reminder_date}' WHERE Id = {message.chat.id}")
                cursor.execute(f"UPDATE people SET One_Reminder = 0 WHERE Id = {message.chat.id}")
                cursor.execute(f"UPDATE people SET Autopayment = {save_payment} WHERE Id = {message.chat.id}")
                connect.commit()
                print(save_payment, "Успех")
                print(payment.payment_method.id)
                return True
    elif payment.status == "pending":
        print(payment.merchant_customer_id)
        return False