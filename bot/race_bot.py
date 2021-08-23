from pyrogram import Client, idle, filters
from pyrogram.types import Message
from state.user_state import *

import tgcrypto
import os
from configparser import ConfigParser
import asyncio

ADMIN_USER = "h_azarbad77"
SUPERVISOR_USERS = ["vahidsavabieh"]
USER_STATES = {}

config = ConfigParser()
config_path = os.path.join(os.getcwd(), 'bot_config.ini')
if not os.path.isfile(config_path):
	raise Exception()
config.read(config_path)
bot_token = config.get('race_bot', 'bot_token')
api_id = config.get('race_bot', 'api_id')
api_hash = config.get('race_bot', 'api_hash')
app = Client('my_bot', bot_token=bot_token, api_hash=api_hash, api_id=api_id)


photo_from_admin_user_filter = filters.create(lambda _, __, query: query.from_user.username == ADMIN_USER)


@app.on_message(filters.new_chat_members | filters.command(['start']))
async def welcome(client: Client, message: Message):
	if message.chat.username in SUPERVISOR_USERS:
		USER_STATES[message.chat.username] = SupervisorInitialState(message.chat.username, app)
		await app.send_message(
			message.chat.id,
			"This is initial of supervisor",
			reply_markup=ReplyKeyboardMarkup(
				[
					["📣  " + "مشاهده نتایج "],  # First row
					["📷  " + "مشاهده عکس مسابقه "],  # Second row
					["⛳  " + "ارزیابی عکس‌ها  "],  # Second row
				],
				resize_keyboard=True  # Make the keyboard smaller
			)
		)
	elif message.chat.username == ADMIN_USER:
		USER_STATES[message.chat.username] = AdminInitialState(message.chat.username, app)
		await app.send_message(
			message.chat.id,
			"This is initial of admin",
			reply_markup=ReplyKeyboardMarkup(
				[
					["📣  " + "مشاهده نتایج "],  # First row
					["📷  " + "مشاهده عکس مسابقه "],  # Second row
					["⛳  " + "پایان مسابقه  "],  # Second row
				],
				resize_keyboard=True  # Make the keyboard smaller
			)
		)
	else:
		USER_STATES[message.chat.username] = NormalUserInitialState(message.chat.username, app)
		await app.send_message(
			message.chat.id,
			"This is example",
			reply_markup=ReplyKeyboardMarkup(
				[
					["📣  " + "مشاهده نتایج "],  # First row
					["📷  " + "مشاهده عکس مسابقه "],  # Second row
					["⛳  " + "ارسال عکس "],  # Second row
				],
				resize_keyboard=True  # Make the keyboard smaller
			)
		)


# Function for normal user and supervisor
@app.on_message(filters.regex("عکس مسابقه") | filters.command(['race_image']))
async def view_race_image(client: Client, message: Message):
	user_state = USER_STATES[message.chat.username] if message.chat.username is not None else None
	try:
		if user_state is not None:
			await user_state.view_race_photo()
	except:
		await user_state.default_function()


# Function for normal user and supervisor and admin
@app.on_message(filters.regex("مشاهده نتایج") | filters.command(['result']))
async def view_result(client: Client, message: Message):
	user_state = USER_STATES[message.chat.username] if message.chat.username is not None else None
	try:
		if user_state is not None:
			await user_state.view_leader_board(leader_board_number=1)
	except:
		await user_state.default_function()


# Function for normal user and supervisor and admin
@app.on_callback_query(filters.regex('leader_board'))
async def f(client, callback_query):
	user_state = USER_STATES[
		callback_query.from_user.username] if callback_query.from_user.username is not None else None
	try:
		if user_state is not None:
			await user_state.view_leader_board(leader_board_number=int(callback_query.data.split("#")[1]))
	except:
		await user_state.default_function()


# Function for normal user
@app.on_message(filters.regex("ارسال عکس") | filters.command(['send_photo']))
async def change_initial_state_to_sending_photo_state(client: Client, message: Message):
	user_state = USER_STATES[message.chat.username] if message.chat.username is not None else None
	if user_state is not None:
		if isinstance(user_state, NormalUserInitialState):
			user_state = user_state.next_state()
			USER_STATES[message.chat.username] = user_state
		await user_state.default_function()


# Function for normal user
@app.on_message(filters.photo & ~photo_from_admin_user_filter)
async def save_user_photo(client: Client, message: Message):
	user_state = USER_STATES[message.chat.username] if message.chat.username is not None else None
	try:
		await user_state.save_user_photo(message)
		user_state = user_state.next_state()
		USER_STATES[message.chat.username] = user_state
		await user_state.default_function()
	except:
		await user_state.default_function()


# Function for supervisor
@app.on_message(filters.regex("ارزیابی عکس‌ها") | filters.command(["evaluation"]))
async def change_initial_state_to_evaluation_state_supervisor(client: Client, message: Message):
	user_state = USER_STATES[message.chat.username] if message.chat.username is not None else None
	if user_state is not None:
		if isinstance(user_state, SupervisorInitialState):
			user_state = await user_state.next_state()
			USER_STATES[message.chat.username] = user_state
		await user_state.default_function()


# Function for supervisor
@app.on_message(filters.regex("تایید") | filters.command(["confirm"]))
async def confirm_photo(client: Client, message: Message):
	user_state = USER_STATES[message.chat.username] if message.chat.username is not None else None
	try:
		if user_state is not None:
			await user_state.confirm_photo()
			user_state = user_state.next_state()
			USER_STATES[message.chat.username] = user_state
			await user_state.default_function()
	except:
		await user_state.default_function()


# Function for supervisor
@app.on_message(filters.regex("رد") | filters.command(["reject"]))
async def confirm_photo(client: Client, message: Message):
	user_state = USER_STATES[message.chat.username] if message.chat.username is not None else None
	try:
		if user_state is not None:
			await user_state.reject_photo()
			user_state = user_state.next_state()
			USER_STATES[message.chat.username] = user_state
			await user_state.default_function()
	except:
		await user_state.default_function()


# Function for admin
@app.on_message(filters.regex("پایان مسابقه") | filters.command(['finish_race']))
async def finish_race(client: Client, message: Message):
	user_state = USER_STATES[message.chat.username] if message.chat.username is not None else None
	try:
		if user_state is not None:
			await user_state.finish_race(USER_STATES)
			user_state = user_state.next_state()
			USER_STATES[message.chat.username] = user_state
			await user_state.default_function()
	except Exception as exception:
		await user_state.default_function()


# Function for admin
@app.on_message(filters.photo & photo_from_admin_user_filter)
async def start_new_race(client: Client, message: Message):
	user_state = USER_STATES[message.chat.username] if message.chat.username is not None else None
	try:
		if user_state is not None:
			await user_state.start_new_race(USER_STATES, message.link, message.photo.file_id)
			user_state = user_state.next_state()
			USER_STATES[message.chat.username] = user_state
			await user_state.default_function()
	except:
		await user_state.default_function()


@app.on_message(filters.all)
async def message_handler(client, message):
	user_state = USER_STATES[message.chat.username] if message.chat.username is not None else None
	if user_state is not None:
		await user_state.default_function()


async def main():
	async with app:
		await idle()


if __name__ == "__main__":
	app.run(main())
