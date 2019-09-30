#coding: utf-8

import os
import random

import vk_api
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id

from flask import Flask, request, json

from vk_config import *
from bad_words import *


# Клавиатура

keyboard = VkKeyboard(one_time=True)

keyboard.add_button('Прикол', color=VkKeyboardColor.POSITIVE)
keyboard.add_button('Рофл', color=VkKeyboardColor.POSITIVE)
keyboard.add_button('Мем', color=VkKeyboardColor.POSITIVE)
keyboard.add_button('Смех', color=VkKeyboardColor.POSITIVE)





# Функция отправки сообщений
MISSING = object()
def write_msg(user_id, message, attachment=MISSING, keyboard=keyboard):
	if attachment is not MISSING:
		# Отправка обычных сообщений
		vk.method('messages.send', {'user_id': user_id, 'message': message, 'attachment': attachment, 'keyboard': keyboard.get_keyboard(), 'random_id': get_random_id()})
		return

	else:
		vk.method('messages.send', {'user_id': user_id, 'message': message, 'keyboard': keyboard.get_keyboard(), 'random_id': get_random_id()})
		return


# Фильтр неприемлемых слов
def is_bad_word(text):
	br_str = text.lower()

	if br_str in bad_words:
		return True

	return False


# Авторизуемся как сообщество
vk = vk_api.VkApi(token=token)

# Интеграция полезных функций из vk_api
tools = vk_api.VkTools(vk)



# Flask
app = Flask(__name__)


@app.route('/', methods=['POST'])
def processing():
	data = json.loads(request.data)
	if 'type' not in data.keys():
		return 'not vk'

	if data['type'] == 'confirmation':
		return confirmation_token

	elif data['type'] == 'message_new':
		user_id = data['object']['user_id']
		message = data['object']['body']

		if is_bad_word(message):
			write_msg(user_id, 'Ошибка: Неприемлемый запрос!', keyboard)

		else:
			# Список последних гифок из вк
			gifs = tools.get_all('docs.search', 100, {'q': message})
			# bot = VkBot(user_id)
				# if message == '/':
				# 	write_msg(user_id, commander.do(message))
			rand_gif = random.choice([i for i in gifs['items'] if i['ext'] == 'gif'])
			doc_file = 'doc{}_{}'.format(
				rand_gif['owner_id'], rand_gif['id']
			)

			write_msg(user_id, 'Ваша гифка!', doc_file, keyboard)

	return 'ok'




if __name__ == '__main__':
	port = int(os.environ.get('PORT', 5000))
	app.run(host='0.0.0.0', port=port)
