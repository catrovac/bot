import telebot
import fake_useragent
import requests
import bs4
from telebot import types
from fake_useragent import UserAgent
import sqlite3
import time
from requests.exceptions import ConnectionError
from urllib3.exceptions import ProtocolError
from conf import tokken, headers, api_id, api_hash

bot = telebot.TeleBot(tokken, True, 4)
bot.config = {'requests_kwargs': {'timeout': 60}, 'api_key': None}
bot.config['api_key'] = tokken

"|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
"|                                                           |"
"|                                                           |"
"|                        OOOOO                              |"
"|                      OO     OO                            |"
"|                      OO                                   |"
"|                      OO                                   |"
"|                      OO                                   |"
"|                      OO     OO                            |"
"|                        OOOOO                              |"
"|                                                           |"
"|                                                           |"
"|              bot by CATROVACER beta-1.2v                  |"
"|____________________________________________________________"

try:
    @bot.message_handler(commands=["start", "help", "auto", "viev"])
    def command_message(message):
        if str(message.text) == '/start':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            key1 = types.KeyboardButton("🔍 - Пробить авто")
            key2 = types.KeyboardButton("ℹ️- Инфо о боте")
            key3 = types.KeyboardButton("🆘 - Помощь")
            key4 = types.KeyboardButton("☕️Розвитие проекта")

            markup.add(key1, key2, key3, key4)
            if str(message.chat.first_name) != None:
                x = "Привет"
                bot.send_message(message.chat.id, x + " " + message.chat.first_name + " "
                                                                                      "/help - тебе поможет"
                                 , parse_mode='Markdown', reply_markup=markup)
            else:
                bot.send_message(message.chat.id, "Привет Аноним", parse_mode='Markdown')
        if str(message.text) == '/help':
            bot.send_message(message.chat.id, "Вот список команд", parse_mode='Markdown')
            x = list_command(message)
            return bot.send_message(message.chat.id, x, parse_mode='Markdown')

        if str(message.text) == "/auto":
            reply = types.InlineKeyboardMarkup()
            yes = types.InlineKeyboardButton(text="Да", callback_data="yes")
            no = types.InlineKeyboardButton(text="Нет", callback_data="no")
            reply.add(yes, no)

            bot.send_message(message.chat.id, "Хотите узнать информацию об автомобиле?", reply_markup=reply,
                             parse_mode='Markdown')


    @bot.callback_query_handler(func=lambda call: True)
    def call_lambda(call):
        if call.data == 'yes':
            msg = bot.send_message(call.message.chat.id, "введите номер автомобиля, (AX6534BI)", parse_mode='Markdown')
            bot.register_next_step_handler(msg, cars_info)
        else:
            bot.send_message(call.message.chat.id, "Очень жаль", parse_mode='Markdown')


    @bot.message_handler(content_types=["text"])
    def incomming_message(message):
        if message.chat.type == "private":
            if str(message.text) == "🔍 - Пробить авто":
                msg = bot.send_message(message.chat.id, "Введите номер авто в формате: АА5425ВІ", parse_mode='Markdown')
                bot.register_next_step_handler(msg, cars_info)
                # print(message.text)
            elif str(message.text) == "ℹ️- Инфо о боте":
                msg = bot.send_message(message.chat.id, "Информация о боте", parse_mode='Markdown')
                bot.register_next_step_handler(msg, bot_info(message))
            else:
                bot.send_message(message.chat.id, "Введите правильный номер", parse_mode='Markdown')


    # bot.polling(none_stop=True)

    def list_command(message):
        commands = ["/start - начало роботы", "/help - помощь", "/viev - информацыя о боте",
                    "/auto - информацыя об авто"]
        x_commands = "\n".join(commands)
        return x_commands


    def bot_info(message):
        return bot.send_message(message.chat.id, "Наш бот берет всю информацию из сайта 'baza-gai.com.ua/' "
                                          "если автомобиль есть в базе то он его найдет и выдаст полную "
                                          "информацию о нем!\n"
                                          "если Вы хотите помочь развитию проекта, нажмите на кнопку Развитие проекта",
                                parse_mode='Markdown')


    def cars_info(message):
        try:
            x = list(str(message.text).upper().split(" "))
            number = "".join(x)
            print(number)
            bot.send_message(message.chat.id, f"Вы ввели {number} сейчас мы найдем необходимую информацию",
                             parse_mode='Markdown')
            # создаем переменную для поиска в Базе ГАИ
            search = f"search?digits={number}"
            rec_url = "https://baza-gai.com.ua/" + search
            # посылаем запрос и получаем ответ сохраняем все в переменную res
            res = requests.get(rec_url, headers=headers).text
            # создаем обьект супа для парсинга
            soup = bs4.BeautifulSoup(res, "lxml")
            # находим необходимые данные (марка автомобиля)
            mark = soup.find("h1", class_="text-center mb-3").text
            mark_auto = mark.strip().split()  # создаем список из названия автомобиля
            mark_auto = ' '.join(mark_auto).strip()  # конкатенируем его в одну строку для удобства
            # находим необходимый список и забираем из него данные про угон сохраняем в переменную ugon
            oll_div = soup.find("div", class_="d-md-none").find_all("div")
            # так же аполучаем номер автомобиля
            num_auto = str(soup.find("div", class_="plate__text").text).strip()
            # переменная с информацыей об угоне
            ugon = str(oll_div[4].text).strip()
            # получаем город розположения автомобиля город регистрации
            city = str(oll_div[3].text).strip()
            operations = str(oll_div[2].text).strip()
            # формируем необходимую строку и сохраняем ее в переменную mess
            if "Не числится" in str(ugon):
                mess = "🚘 - " + str(mark_auto) + "\n" + "#️⃣ - " + str(num_auto).strip() + "\n" + "✅ - " + str(
                    ugon) + "\n" + "🌆 - " + str(city) + "\n" + "📝 - " + str(operations)
                rep = types.InlineKeyboardMarkup()
                yes = types.InlineKeyboardButton(text="Да", callback_data="yes")
                no = types.InlineKeyboardButton(text="Нет", callback_data="no")
                rep.add(yes, no)
                return bot.send_message(message.chat.id, f"вот что мы нашли по номеру {number} \n\n {mess} \n\n"
                                                         f"хотите узнать еще один автомобиль?", reply_markup=rep,
                                        parse_mode='Markdown')
            else:
                mess = "🚘 - " + str(mark_auto) + "\n" + "#️⃣ - " + str(num_auto).strip() + "\n" + "❌ - " + str(
                    ugon) + "\n" + "🌆 - " + str(city) + "\n" + "📝 - " + str(operations)
                return bot.send_message(message.chat.id, f"вот что мы нашли по номеру {number} \n {mess}",
                                        parse_mode='Markdown')
        except IndexError as index:
            print(index)
            rep = types.InlineKeyboardMarkup()
            yes = types.InlineKeyboardButton(text="Да", callback_data="yes")
            no = types.InlineKeyboardButton(text="Нет", callback_data="no")
            rep.add(yes, no)
            return bot.send_message(message.chat.id, "НЕ найдено, попробуйте еще",
                                    parse_mode='Markdown', reply_markup=rep)
        except AttributeError as atr:
            print(atr)
            rep = types.InlineKeyboardMarkup()
            yes = types.InlineKeyboardButton(text="Да", callback_data="yes")
            no = types.InlineKeyboardButton(text="Нет", callback_data="no")
            rep.add(yes, no)
            return bot.send_message(message.chat.id,
                                    f"НЕ найдено совпадений по номеру {number}, попробовать еще",
                                    parse_mode='Markdown', reply_markup=rep)

except requests.exceptions.ConnectionError as conn:
    print(conn)
except TypeError as typemessage:
    print(typemessage)
if __name__ == "__main__":
    bot.infinity_polling()
