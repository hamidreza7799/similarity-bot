import os
import sys

sys.path.insert(1, os.path.normpath(os.getcwd() + os.sep + os.pardir))
from pyrogram import idle, filters
from state.user_state import *
from storage.backup import BackupDriver
from race_config import ADMIN_USER, SUPERVISOR_USERS, photo_from_admin_user_filter, api_id, api_hash, bot_token, \
	SUPERVISOR_INITIAL_KEYBOARD, ADMIN_INITIAL_KEYBOARD, NORMAL_USER_INITIAL_KEYBOARD, BACKUP_MINUTES
import tgcrypto
import asyncio
import threading

USER_STATES = {}
app = Client('config/my_bot', bot_token=bot_token, api_hash=api_hash, api_id=api_id)
LOCK_RACE = True
LOCK_RACE_ASYNC_LOCK = asyncio.Lock()


@app.on_message(filters.new_chat_members | filters.command(['start']))
async def welcome(_, message: Message):
	global LOCK_RACE
	async with LOCK_RACE_ASYNC_LOCK:
		if message.chat.id in SUPERVISOR_USERS:
			if LOCK_RACE:
				USER_STATES[message.chat.id] = SupervisorLockState(message.chat.id, app)
				await app.send_message(
					message.chat.id,
					"This is text in initial state for supervisor",
					reply_markup=ReplyKeyboardRemove()
				)
			else:
				USER_STATES[message.chat.id] = SupervisorInitialState(message.chat.id, app)
				await app.send_message(
					message.chat.id,
					"This is text in initial state for supervisor",
					reply_markup=SUPERVISOR_INITIAL_KEYBOARD
				)
		elif message.chat.id == ADMIN_USER:
			if LOCK_RACE:
				USER_STATES[message.chat.id] = AdminWaitForStartNewRace(message.chat.id, app)
				await app.send_message(
					message.chat.id,
					"This is initial text of admin",
					reply_markup=ReplyKeyboardRemove()
				)
			else:
				USER_STATES[message.chat.id] = AdminInitialState(message.chat.id, app)
				await app.send_message(
					message.chat.id,
					"This is initial of admin",
					reply_markup=ADMIN_INITIAL_KEYBOARD
				)
		else:
			if LOCK_RACE:
				USER_STATES[message.chat.id] = NormalUserLockState(message.chat.id, app)
				await app.send_message(
					message.chat.id,
					"This is initial for normal user",
					reply_markup=ReplyKeyboardRemove()
				)
			else:
				USER_STATES[message.chat.id] = NormalUserInitialState(message.chat.id, app)
				await app.send_message(
					message.chat.id,
					"This is initial for normal user",
					reply_markup=NORMAL_USER_INITIAL_KEYBOARD
				)


# Function for normal user and supervisor and admin
@app.on_message(filters.regex("بازگشت") | filters.command(['back']))
async def back_current_user_state(_, message: Message):
	user_state = USER_STATES[message.chat.id] if message.chat.id in USER_STATES else None
	try:
		if user_state is not None:
			USER_STATES[message.chat.id] = user_state.back_state()
			await USER_STATES[message.chat.id].default_function()
		else:
			await welcome(_, message)
	except:
		await user_state.default_function()


# Function for normal user and supervisor and admin
@app.on_message(filters.regex("عکس مسابقه") | filters.command(['race_image']))
async def view_race_image(_, message: Message):
	user_state = USER_STATES[message.chat.id] if message.chat.id in USER_STATES else None
	try:
		if user_state is not None:
			await user_state.view_race_photo()
		else:
			await welcome(_, message)
	except:
		await user_state.default_function()


# Function for normal user and supervisor and admin
@app.on_message(filters.regex("مشاهده نتایج") | filters.command(['result']))
async def view_result(_, message: Message):
	user_state = USER_STATES[message.chat.id] if message.chat.id in USER_STATES else None
	try:
		if user_state is not None:
			await user_state.view_leader_board(leader_board_number=1)
		else:
			await welcome(_, message)
	except Exception as error:
		await user_state.default_function()


# Function for normal user and supervisor and admin
@app.on_callback_query(filters.regex('leader_board'))
async def f(_, callback_query):
	user_state = USER_STATES[
		callback_query.from_user.id] if callback_query.from_user.id in USER_STATES else None
	try:
		if user_state is not None:
			await user_state.view_leader_board(leader_board_number=int(callback_query.data.split("#")[1]))
		else:
			await welcome(_, callback_query.message)
	except:
		await user_state.default_function()


# Function for normal user
@app.on_message(filters.regex("ارسال عکس") | filters.command(['send_photo']))
async def change_initial_state_to_sending_photo_state(_, message: Message):
	user_state = USER_STATES[message.chat.id] if message.chat.id in USER_STATES else None
	try:
		if user_state is not None:
			sending_photo_state = user_state.change_to_sending_photo_state()
			USER_STATES[message.chat.id] = sending_photo_state
			sending_photo_state.default_funtion()
		else:
			await welcome(_, message)
	except:
		await user_state.default_function()


# Function for normal user
@app.on_message(filters.photo & ~photo_from_admin_user_filter)
async def save_user_photo(_, message: Message):
	user_state = USER_STATES[message.chat.id] if message.chat.id in USER_STATES else None
	try:
		aipa_state = user_state.save_user_photo()
		USER_STATES[message.chat.id] = aipa_state
		await aipa_state.work_with_aipa(message)
		user_state = aipa_state.next_state()
		USER_STATES[message.chat.id] = user_state
		await user_state.default_function()
	except Exception as error:
		await user_state.default_function()


# Function for supervisor
@app.on_message(filters.regex("ارزیابی عکس‌ها") | filters.command(["evaluation"]))
async def change_initial_state_to_evaluation_state_supervisor(_, message: Message):
	user_state = USER_STATES[message.chat.id] if message.chat.id in USER_STATES else None
	try:
		if user_state is not None:
			evaluation_state = user_state.change_to_evaluation_state()
			USER_STATES[message.chat.id] = evaluation_state
			evaluation_state.dafault_function()
		else:
			await welcome(_, message)
	except:
		await user_state.dafault_function()


# Function for supervisor
@app.on_message(filters.regex("تایید") | filters.command(["confirm"]))
async def confirm_photo(_, message: Message):
	user_state = USER_STATES[message.chat.id] if message.chat.id in USER_STATES else None
	try:
		if user_state is not None:
			user_state.confirm_photo()
			user_state = user_state.next_state()
			USER_STATES[message.chat.id] = user_state
			await user_state.default_function()
		else:
			await welcome(_, message)
	except:
		await user_state.default_function()


# Function for supervisor
@app.on_message(filters.regex("رد") | filters.command(["reject"]))
async def reject_photo(_, message: Message):
	user_state = USER_STATES[message.chat.id] if message.chat.id in USER_STATES else None
	try:
		if user_state is not None:
			user_state.reject_photo()
			user_state = user_state.next_state()
			USER_STATES[message.chat.id] = user_state
			await user_state.default_function()
		else:
			await welcome(_, message)
	except:
		await user_state.default_function()


# Function for admin
@app.on_message(filters.regex("پایان مسابقه") | filters.command(['finish_race']))
async def finish_race(_, message: Message):
	global LOCK_RACE
	user_state = USER_STATES[message.chat.id] if message.chat.id in USER_STATES else None
	async with LOCK_RACE_ASYNC_LOCK:
		try:
			if user_state is not None:
				LOCK_RACE = True
				await user_state.finish_race(USER_STATES)
				user_state = user_state.next_state()
				USER_STATES[message.chat.id] = user_state
				await user_state.default_function()
			else:
				await welcome(_, message)
		except Exception as exception:
			LOCK_RACE = False
			await user_state.default_function()


# Function for admin
@app.on_message(filters.photo & photo_from_admin_user_filter)
async def start_new_race(_, message: Message):
	global LOCK_RACE
	user_state = USER_STATES[message.chat.id] if message.chat.id in USER_STATES else None
	async with LOCK_RACE_ASYNC_LOCK:
		try:
			if user_state is not None:
				LOCK_RACE = False
				await user_state.start_new_race(USER_STATES, message)
				user_state = user_state.next_state()
				USER_STATES[message.chat.id] = user_state
				await user_state.default_function()
			else:
				await welcome(_, message)
		except Exception as error:
			LOCK_RACE = True
			await user_state.default_function()


@app.on_message(filters.all)
async def message_handler(_, message: Message):
	user_state = USER_STATES[message.chat.id] if message.chat.id in USER_STATES else None
	if user_state is not None:
		await user_state.default_function()
	else:
		await welcome(_, message)


async def main():
	async with app:
		await idle()


def backup_user_states():
	user_states_json_file_path = os.path.join(os.getcwd(), 'backup', "user_states.json")
	BackupDriver.backup_user_states(user_states_json_file_path, USER_STATES.copy())
	threading.Timer(BACKUP_MINUTES * 60, backup_user_states).start()


if __name__ == "__main__":
	threading.Timer(BACKUP_MINUTES * 60, backup_user_states).start()
	app.run(main())
