import wikipedia as wiki
from wikipedia import DisambiguationError
import telebot
from telebot import types
import config as cfg
import warnings

warnings.filterwarnings("ignore")

bot = telebot.TeleBot(cfg.token)
resources = ['wikipedia']


@bot.message_handler(commands=['start'])
def start(message):
    try:
        # todo: Переделать приветствие
        bot.send_message(message.chat.id, 'Привет, я "ВикиБот", бот, '
                                          'который призван облегчить поиск нужной информации. '
                                          'Для поиска ты можешь воспользоваться функцией /search')
    except Exception as e:
        bot.send_message(message.chat.id, f'Ошибка, {e}')


@bot.message_handler(commands=['help'])
def help(message):
    try:
        # todo: Дописать список доступных команд
        bot.send_message(message.chat.id, 'Список доступных команд\n'
                                          '1. /search - Поиск информации')
    except Exception as e:
        bot.send_message(message.chat.id, f'Ошибка, {e}')


@bot.message_handler(commands=['search'])
def search(message):
    try:
        msg = bot.send_message(message.chat.id, 'Напиши то, что хочешь найти')
        bot.register_next_step_handler(msg, searching)
    except Exception as e:
        bot.send_message(message.chat.id, f'Ошибка, {e}')


def searching(message):
    try:
        if message.text is not None:
            answrs = 0
            code = wiki_search(message)
            if code == 0:
                # todo:
                kb_resources = types.InlineKeyboardMarkup(row_width=2)
                with open(f'answers/{message.from_user.id}.txt', 'r', encoding="utf-8") as answr:
                    lines = answr.readlines()
                    for line in lines:
                        if line.strip() in resources:
                            # todo: Сделать список [ресурс: callback], чтобы можно было добавлять больше 1 кнопки в ряд
                            #       и создавать клавиатуру сразу
                            kb_resources.add(
                                types.InlineKeyboardButton(text=line, callback_data=f'ans {line} {str(message.from_user.id)}'))
                            answrs += 1

                bot.send_message(message.chat.id, f'Найдено {answrs} ответов', reply_markup=kb_resources)
        else:
            msg = bot.send_message(message.chat.id,
                                   'Мне кажется или это не похоже на текст. '
                                   'Даю ещё попытку, попробуй попасть по клавиатуре')
            bot.register_next_step_handler(msg, searching)

    except Exception as e:
        bot.send_message(message.chat.id, f'Ошибка, {e}')


def wiki_search(message):
    try:
        wiki.set_lang("ru")
        srch = wiki.search(message.text)
        sm = wiki.summary(srch[0])
        ans = sm.split('\n')[0]

        with open(f'answers/{message.from_user.id}.txt', 'w', encoding="utf-8") as answr:
            answr.writelines(['wikipedia\n', '*\n', ans, '\n', '*\n'])

        return 0

    except DisambiguationError as e:
        choise = str(e).split("\n")[1:]
        choise = [f'<code>{i}</code>' for i in choise]
        choise = '\n'.join(choise)

        msg = bot.send_message(message.chat.id, f'Возможно вы имели в виду что-то из нижеперечисленного\n\n{choise}',
                               parse_mode='HTML')

        bot.register_next_step_handler(msg, searching)
        return 1

    except IndexError as e:
        msg = bot.send_message(message.chat.id, 'По вашему запросу ничего не найдено')


@bot.message_handler(content_types=['text'])
def mistake(message):
    try:
        msg = bot.send_message(message.chat.id, 'Прости, я тебя не понимаю. '
                                                'Ты можешь посмотреть список доступных команд /help')
    except Exception as e:
        bot.send_message(message.chat.id, f'Ошибка, {e}')


@bot.message_handler(content_types=['animation', 'audio', 'contact', 'dice', 'document', 'location', 'photo', 'poll',
                                    'sticker', 'text', 'venue', 'video', 'video_note', 'voice'])
def wrong_message(message: types.Message):
    try:
        bot.send_message(message.chat.id, 'Прости, я не могу обработать это сообщение, попробуй что-нибудь другое')
    except Exception as e:
        bot.send_message(message.chat.id, f'Ошибка, {e}')


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if str(call.data).startswith('ans'):
        with open(f'answers/{call.from_user.id}.txt', 'r', encoding="utf-8") as answr:
            ans = ''.join([i.strip() for i in answr.readlines()]).split('*')
        # очистка файла
        with open(f'answers/{call.from_user.id}.txt', 'w', encoding="utf-8"):
            pass
        res = str(call.data).split()[1]
        msg = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                    text=ans[ans.index(res) + 1])


bot.polling()
