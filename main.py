from telegram import Update
from telegram import Bot, ReplyKeyboardMarkup
from telegram.ext import Updater, MessageHandler, Filters
import pickle
from datetime import datetime


# global values
bot_token = '1908851765:AAGU9ODojJPWpUARHnwfcmz9xYRufxTGXRI'
users = {}
menuStates = {}
menuStates['default'] = 0
menuStates['waitProductName'] = 1
menuStates['waitProductPrice'] = 2
menuStates['waitProductPart'] = 3
menuStates['waitProductDate'] = 4
menuStates['waitNumToDel'] = 5
menuStates['waitAddPartName'] = 6
menuStates['waitMonthNum'] = 7
menuStates['waitDelPartName'] = 8

savesFileName = 'db.dat'
dateMenu = ReplyKeyboardMarkup([['today']])
mainMenu = ReplyKeyboardMarkup([['expenses', 'add_exp', 'del_exp'], ['parts', 'add_pt', 'del_pt'], ['me']])
monthMenu = ReplyKeyboardMarkup([['1', '2', '3', '4'], ['5', '6', '7', '8'], ['9', '10', '11', '12']])
bot = Bot(token=bot_token)
# user_id = 964090213


def getSaves():
    global users
    try:
        with open(savesFileName, 'rb') as file:
            users = pickle.load(file)
        print(users)
    except Exception as e:
        print(e)


def save():
    with open(savesFileName, 'wb') as file:
        pickle.dump(users, file)


def get_message(update: Update, context):
    global users
    user_id = update.message.chat.id
    msg = update.message.text

    print(user_id, msg)
    if user_id in users:
        try:
            if 'add_exp' in msg:
                bot.send_message(user_id, 'Введите название покупки')
                users[user_id]['menuState'] = menuStates['waitProductName']
                users[user_id]['buffer'] = {}
            elif 'del_exp' in msg:
                bot.send_message(user_id, 'Напишите номер покупки который хотите удалить')
                users[user_id]['menuState'] = menuStates['waitNumToDel']
            elif 'me' in msg:
                bot.send_message(user_id, str(users[user_id]))
                users[user_id]['menuState'] = menuStates['default']
            elif 'expenses' in msg:
                out = ''
                for month in users[user_id]['expenses']:
                    out += str(month) + ' месяц - ' + str(users[user_id]['expenses'][month]['sum']) + '\n'
                    for day in users[user_id]['expenses'][month]['days']:
                        out += '     ' + str(day) + ' - ' + str(users[user_id]['expenses'][month]['days'][day]['sum']) + '\n'
                        for prodId in users[user_id]['expenses'][month]['days'][day]:
                            if prodId == 'sum':
                                continue
                            out += '         ' + users[user_id]['expenses'][month]['days'][day][prodId]['name'] +\
                                   ' - ' + str(users[user_id]['expenses'][month]['days'][day][prodId]['price']) +\
                                   ' (/' + str(prodId) + ')\n'
                        out += '\n'
                    out += '\n'
                if out == '':
                    out = 'Мне нечего сказать('
                bot.send_message(user_id, out, reply_markup=None)
            elif 'add_pt' in msg:
                bot.send_message(user_id, 'Введите название части')
                users[user_id]['menuState'] = menuStates['waitAddPartName']
            elif 'del_pt' in msg:
                buttons = []
                for part in users[user_id]['parts']:
                    buttons.append([part])
                partsMenu = ReplyKeyboardMarkup(buttons)
                bot.send_message(user_id, 'Выберите название раздела', reply_markup=partsMenu)
                users[user_id]['menuState'] = menuStates['waitDelPartName']
            elif 'part' in msg:
                bot.send_message(user_id, 'Выберите месяц', reply_markup=monthMenu)
                users[user_id]['menuState'] = menuStates['waitMonthNum']
            else:
                if users[user_id]['menuState'] == menuStates['waitProductName']:
                    users[user_id]['buffer']['name'] = msg
                    bot.send_message(user_id, 'Введите цену')
                    users[user_id]['menuState'] = menuStates['waitProductPrice']
                elif users[user_id]['menuState'] == menuStates['waitProductPrice']:
                    users[user_id]['buffer']['price'] = float(msg)
                    buttons = []
                    for part in users[user_id]['parts']:
                        buttons.append([part])
                    partsMenu = ReplyKeyboardMarkup(buttons)
                    bot.send_message(user_id, 'Выберите раздел', reply_markup=partsMenu)
                    users[user_id]['menuState'] = menuStates['waitProductPart']
                elif users[user_id]['menuState'] == menuStates['waitProductPart']:
                    users[user_id]['buffer']['part'] = msg
                    bot.send_message(user_id, 'Введите дату (DD.MM)', reply_markup=dateMenu)
                    users[user_id]['menuState'] = menuStates['waitProductDate']
                elif users[user_id]['menuState'] == menuStates['waitProductDate']:
                    if msg == 'today':
                        day = datetime.now().day
                        month = datetime.now().month
                    else:
                        day = int(msg[:msg.find('.')])
                        month = int(msg[msg.find('.')+1:])
                    if not (month in users[user_id]['expenses']):
                        users[user_id]['expenses'][month] = {'sum': 0, 'days': {}}
                    if not (day in users[user_id]['expenses'][month]['days']):
                        users[user_id]['expenses'][month]['days'][day] = {'sum': 0}
                    nowId = users[user_id]['prodId']
                    users[user_id]['expenses'][month]['days'][day][nowId] = {}
                    users[user_id]['expenses'][month]['days'][day][nowId]['name'] = users[user_id]['buffer']['name']
                    users[user_id]['expenses'][month]['days'][day][nowId]['price'] = users[user_id]['buffer']['price']
                    users[user_id]['expenses'][month]['days'][day][nowId]['part'] = users[user_id]['buffer']['part']
                    users[user_id]['expenses'][month]['sum'] += users[user_id]['buffer']['price']
                    users[user_id]['expenses'][month]['sum'] = round(users[user_id]['expenses'][month]['sum'], 2)
                    users[user_id]['expenses'][month]['days'][day]['sum'] += users[user_id]['buffer']['price']
                    users[user_id]['expenses'][month]['days'][day]['sum'] = round(users[user_id]['expenses'][month]['days'][day]['sum'], 2)
                    users[user_id]['buffer'] = {}
                    users[user_id]['prodId'] += 1
                    bot.send_message(user_id, 'Всё готово', reply_markup=mainMenu)
                    users[user_id]['menuState'] = menuStates['default']
                    keys = sorted(users[user_id]['expenses'][month]['days'].keys())
                    temp = users[user_id]['expenses'][month]['days'].copy()
                    users[user_id]['expenses'][month]['days'] = {}
                    for key in keys:
                        users[user_id]['expenses'][month]['days'][key] = temp[key]
                elif users[user_id]['menuState'] == menuStates['waitNumToDel']:
                    if '/' in msg:
                        msg = msg[1:]
                    msg = int(msg)
                    for month in users[user_id]['expenses']:
                        for day in users[user_id]['expenses'][month]['days']:
                            if msg in users[user_id]['expenses'][month]['days'][day]:
                                users[user_id]['expenses'][month]['days'][day]['sum'] -= users[user_id]['expenses'][month]['days'][day][msg]['price']
                                users[user_id]['expenses'][month]['sum'] -= users[user_id]['expenses'][month]['days'][day][msg]['price']
                                del users[user_id]['expenses'][month]['days'][day][msg]
                                break
                    users[user_id]['menuState'] = menuStates['default']
                    bot.send_message(user_id, 'Успешно удалено')
                elif users[user_id]['menuState'] == menuStates['waitAddPartName']:
                    users[user_id]['parts'].append(msg)
                    users[user_id]['menuState'] = menuStates['default']
                    bot.send_message(user_id, 'Раздел добавлен', reply_markup=mainMenu)
                elif users[user_id]['menuState'] == menuStates['waitMonthNum']:
                    out = ''
                    parts = {}
                    sm = users[user_id]['expenses'][int(msg)]['sum']
                    for part in users[user_id]['parts']:
                        parts[part] = 0
                    for day in users[user_id]['expenses'][int(msg)]['days']:
                        for prodId in users[user_id]['expenses'][int(msg)]['days'][day]:
                            if prodId == 'sum':
                                continue
                            parts[users[user_id]['expenses'][int(msg)]['days'][day][prodId]['part']] += \
                                users[user_id]['expenses'][int(msg)]['days'][day][prodId]['price']
                            parts[users[user_id]['expenses'][int(msg)]['days'][day][prodId]['part']] =\
                                round(parts[users[user_id]['expenses'][int(msg)]['days'][day][prodId]['part']], 2)
                    out += 'Итог: ' + str(sm) + '\n'
                    for part in parts:
                        out += '-' + str(part) + ' - ' + str(parts[part]) + ' - ' + str(round(parts[part] * 100 / sm)) + '%\n'
                    bot.send_message(user_id, out, reply_markup=mainMenu)
                    users[user_id]['menuState'] = menuStates['default']
                elif users[user_id]['menuState'] == menuStates['waitDelPartName']:
                    del users[user_id]['parts'][users[user_id]['parts'].index(msg)]
                    bot.send_message(user_id, 'Удалено успешно', reply_markup=mainMenu)
                    users[user_id]['menuState'] = menuStates['default']
                else:
                    bot.send_message(user_id, 'Ничего не понял', reply_markup=mainMenu)
        except Exception as e:
            print('Error: ' + str(e))
            bot.send_message(user_id, 'Error\n' + str(e), reply_markup=mainMenu)
            users[user_id]['menuState'] = menuStates['default']
    else:
        users[user_id] = {'parts': ['Другое'], 'expenses': {}, 'menuState': 0, 'buffer': {}, 'prodId': 0}
        bot.send_message(user_id, 'Вы добавлены в систему', reply_markup=mainMenu)
    save()


def main():
    getSaves()
    updater = Updater(bot_token)
    updater.dispatcher.add_handler(MessageHandler(Filters.text, get_message))
    updater.start_polling()
    print('Started')
    updater.idle()


if __name__ == "__main__":
    main()
