import fake_useragent
import requests
from selenium import webdriver
import telebot
from telebot import types
from bs4 import BeautifulSoup
from settings import tokken
from db_bot import data_base_bot
import time
#from payments import Payments


class Request(object):
    headers = {"user-agent": fake_useragent.UserAgent().data_browsers["chrome"][0]}

    def request_from(self):
        url = f"https://baza-gai.com.ua/nomer/{self.number}"
        result = requests.get(url, headers=self.headers)
        if result.status_code == 200:
            with open('index.html', 'w', encoding='utf-8') as file:
                file.write(result.text)

            soup = BeautifulSoup(result.text, "lxml")
            try:
                vin = soup.find('span', id='vin-code-erased').get('data-full')

            except Exception as _ex:
                vin = 'Vin код не указан'
            vin = "VIN : " + vin
            all_info = soup.find("tbody").find_all("td")
            date = f"ДАТА РЕГИСТРАЦИИ : {str(all_info[0].text).strip()}"
            mark = ' '.join(str(all_info[1].text).split())
            mark = 'МАРКА : ' + mark
            dvig = str(all_info[2].text)
            dvig = "ЦВЕТ И ОБЬЕМ : " + dvig
            info = ' '.join(str(all_info[3].text).split())
            info = 'ОПИСАНИЕ : ' + info
            user_info = all_info[4].text
            user_info = "ИНФОРМАЦИЯ : " + user_info
            stolen = str(soup.find('div', class_='stolen-info').text).strip()
            stolen = "ОБ УГОНЕ : " + stolen
            photo = soup.find('div', class_='text-center mt-3 mx-auto').find('img').get('src')
            imge_url = 'https://baza-gai.com.ua' + photo
            result_image = requests.get(imge_url, headers=self.headers).content
            with open('1.jpg', "wb") as file:
                file.write(result_image)
            return mark, date, vin, dvig, info, user_info, stolen


client = telebot.TeleBot(tokken)

command_list = ['/start - начало роботы', '/info - информация о боте', '/auto - найти автомобиль', '/abouth - о нас']


@client.message_handler(commands=['start', 'info', 'auto', 'abouth'])
def tele_commands(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    key1 = types.KeyboardButton("🔍 - Пробить авто")
    key2 = types.KeyboardButton("ℹ️- Инфо о боте")
    key3 = types.KeyboardButton("🆘 - Помощь")
    #key4 = types.KeyboardButton("☕️Розвитие проекта")

    markup.add(key1, key2, key3)
    if message.text == '/start'.lower():
        try:
            username = message.json['from']['first_name']
            mess = f"Привет {username}! \nэтот бот ищет информацию об авто в Украине 🇺🇦" \
                   f"для получения списка комманд 👉 /info 👈"
            # print(username)
        except Exception as use:
            username = "Username"
        client.send_message(message.chat.id, mess, reply_markup=markup)
    elif message.text == '/info'.lower():
        x = 'Бот находится в тестовом режиме 🛠\n'
        mess = f'{x}Список доступных команд\n' + '\n'.join(command_list)
        client.send_message(message.chat.id, mess)
    elif message.text == '/auto'.lower():
        msg = client.send_message(message.chat.id, "введите номер автомобиля, (AX6534BI)")
        client.register_next_step_handler(msg, cars_info)
    elif message.text == '/abouth'.lower():
        mess = """
        Привет друг,\n Мы молодая команда создающая полезные вещи для людей!\nВся информация взята с базы данных ГАИ
и актуальна начегоднешний день!\nБлагодарим за пользование нашими услугами.
        """
        client.send_message(message.chat.id, str(mess).strip())


@client.callback_query_handler(func=lambda call: True)
def call_lambda(call):
    if call.data == 'yes':
        msg = client.send_message(call.message.chat.id, "введите номер автомобиля, (AX6534BI)", parse_mode='Markdown')
        client.register_next_step_handler(msg, cars_info)
    else:
        client.send_message(call.message.chat.id, "Очень жаль", parse_mode='Markdown')


@client.message_handler(content_types=['text'])
def mess_from_user(message):
    if message.text == "🔍 - Пробить авто":
        msg = client.send_message(message.chat.id, 'Введите номер автомобиля в формате (АА6565BI)')
        client.register_next_step_handler(msg, cars_info)
    elif message.text == "ℹ️- Инфо о боте":
        x = 'Бот находится в тестовом режиме 🛠\n'
        mess = f'{x}Список доступных команд\n' + '\n'.join(command_list)
        client.send_message(message.chat.id, mess)
    elif message.text == "🆘 - Помощь":
        mess = """
Привет друг,\n этот бот может найти информацию об автомобиле в Украине!
для этого необходимо отправить команду /auto и ввести номер автомобиля.
Вся информация взята с базы данных ГАИ
и актуальна на сегоднешний день!
                """
        client.send_message(message.chat.id, str(mess).strip())
    #elif message.text == "☕️Розвитие проекта":
    #    client.send_message(message.chat.id, f"платежная система пока в розработке\n"
    #                                         f"но при желании можете перевести на карту\n"
    #                                         f"(Приват банк)")
    #    client.send_message(message.chat.id, "4149 6293 1594 0247")
        #Payments.user_pay(self=Payments,client=client, chat_id=message.chat.id)


def cars_info(message):
    data_base_bot(message)
    try:
        print(message.text)
        # ниже привденный код робочий
        Request.number = str(message.text).upper()
        req = Request.request_from(self=Request)
        mess = '\n'.join(req)
        rep = types.InlineKeyboardMarkup()
        yes = types.InlineKeyboardButton(text="Да", callback_data="yes")
        no = types.InlineKeyboardButton(text="Нет", callback_data="no")
        rep.add(yes, no)
        client.send_message(message.chat.id, mess)
        client.send_message(message.chat.id, "Фото взято с базы ГАИ цвет на фото может не соответствовать указанному")
        client.send_photo(message.chat.id, photo=open('1.jpg', 'rb'))
        client.send_message(message.chat.id, "Хотите пробить еще автомобиль", reply_markup=rep)
    except Exception as _ex:
        client.send_message(message.chat.id, f'Вы ввели номер {str(message.text).upper()} '
                                             f'проверте правельность ввода номера')


def main():
    client.polling(non_stop=True)


if __name__ == '__main__':
    main()
