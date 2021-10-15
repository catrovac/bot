import sqlite3
from time import sleep as sl


def data_base_bot(message):
    count = 0
    user_id = str(message.json['from']['id'])
    try:
        first_name = str(message.json['from']['first_name'])
    except Exception:
        first_name = "first_Username"
    try:
        last_name = str(message.json['from']['last_name'])
    except Exception:
        last_name = "last_username"

    # print(user_id, first_name, last_name)

    db = sqlite3.connect('bot_user.db')
    cursor = db.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS users(id INT PRIMARY KEY,
                                                            first_name text NOT NULL,
                                                            last_name text NOT NULL,
                                                            user_chat_id INTEGER UNIQUE,
                                                            counts INT)""")
    db.commit()
    add_user(db, first_name, last_name, user_id)

    # print(message.json['from'])


def add_user(db, first_name, last_name, user_id):
    try:
        counte = 1
        cursor = db.cursor()
        data = cursor.execute("""SELECT id, user_chat_id FROM users""")
        user_list = data.fetchall()
        is_user = int(user_list[-1][0]) + counte
        cursor.execute("""INSERT INTO users VALUES(?,?,?,?,?)""", (is_user, first_name, last_name, user_id, counte))
        db.commit()
        print(f"[INFO] new user added to DATA_BASE first_name is {first_name} USER_ID is {user_id}")
    except Exception:
        for name in user_list:
            if int(name[1]) == int(user_id):
                data_count = cursor.execute(f"""SELECT counts FROM users WHERE id = {name[0]}""")
                users_count = data_count.fetchall()[0][0]
                #print(users_count)
                count = int(users_count) + 1
                update = f"""UPDATE users SET counts = {count} WHERE id = {name[0]}"""
                cursor.execute(update)
                db.commit()
                db.close()
                print(f"[INFO] ->update count is {count} user requests updated<-\n"
                      f"[INFO] ->DATA_BASE is closed<-")
