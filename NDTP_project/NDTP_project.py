from re import search
import telebot

bot = telebot.TeleBot('6157578435:AAEnF4_LW2PD0utagpOLsv4jXNqwI_wX93c')

main_menu_keyboard = telebot.types.ReplyKeyboardMarkup(True)
main_menu_keyboard.row('�����', '�������� �����')

search_keyboard = telebot.types.ReplyKeyboardMarkup(True)
search

@bot.message_handler(commands=['start'])
def start_command_reply(message):
    bot.send_message(message.chat.id, '����� ��� ��, ��� ����� ���� ���', reply_markup=main_menu_keyboard)


@bot.message_handler(content_types=['text'])
def text_handler(message):
    text = message.text.capitalize()
    if text == '�����':
        bot.send_message(message.chat.id, reply_markup=search_keyboard)
