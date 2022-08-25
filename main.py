import wikipedia as wiki
from wikipedia import DisambiguationError
import telebot
from telebot import types
import config as cfg
import warnings

warnings.filterwarnings("ignore")

bot = telebot.TeleBot(cfg.token)


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
            wiki.set_lang("ru")
            srch = wiki.search(message.text)
            sm = wiki.summary(srch[0])
            ans = sm.split('\n')[0]
            bot.send_message(message.chat.id, f'{ans}')
        else:
            msg = bot.send_message(message.chat.id,
                                   'Мне кажется или это не похоже на текст. '
                                   'Даю ещё попытку, попробуй попасть по клавиатуре')
            bot.register_next_step_handler(msg, searching)
    except DisambiguationError as e:
        choise = "\n".join(str(e).split("\n")[1:])
        msg = bot.send_message(message.chat.id, f'Возможно вы имели в виду что-то из нижеперечисленного\n\n{choise}')
        bot.register_next_step_handler(msg, searching)
    except IndexError as e:
        msg = bot.send_message(message.chat.id, f'По вашему запросу "{message.text}" ничего не найдено. '
                                                f'Попробуйте что-нибудь другое')
        bot.register_next_step_handler(msg, searching)


@bot.message_handler(content_types=['text'])
def mistake(message):
    try:
        msg = bot.send_message(message.chat.id, 'Прости, я тебя не понимаю. '
                                                'Ты можешь посмотреть список доступных команд /help')
    except Exception as e:
        bot.send_message(message.chat.id, f'Ошибка, {e}')


@bot.message_handler(content_types=['animation', 'audio', 'contact', 'dice', 'document', 'location', 'photo', 'poll', 'sticker', 'text', 'venue', 'video', 'video_note', 'voice'])
def wrong_message(message: types.Message):
    try:
        bot.send_message(message.chat.id, 'Прости, я не могу обработать это сообщение, попробуй что-нибудь другое')
    except Exception as e:
        bot.send_message(message.chat.id, f'Ошибка, {e}')


bot.polling()
