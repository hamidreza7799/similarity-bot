from abc import ABC, abstractmethod
from pyrogram.types import Message
from pyrogram import Client
from pyrogram.types import (InlineQueryResultArticle, InputTextMessageContent,
                            InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove)
from pyrogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from pykeyboard import InlineKeyboard
from storage.data import *
from aipa.aipa import *
import asyncio
import os
import json

from bot.race_bot import ADMIN_USER, SUPERVISOR_USERS

AIPA_CLIENT = AipaRestClient()
AIPA_CLIENT.get_valid_access_token()
RACE_PHOTO_MEDIA_LINK = "https://t.me/c/-1000925175130/252"
RACE_PHOTO_MEDIA_FILE_ID = "AgACAgQAAxkBAAP8YSDEOnTz3YlFV0BrkEi-4ponqG8AAva1MRvPXAhR8geW3vrqkFddxrUvXQADAQADAgADeQAD88wCAAEeBA"
RACE_PHOTO_FILE = "Ronaldo"
LEADER_BOARD_MAX_LENGTH = 10
MINIMUM_SCORE_IN_LEADER_BOARD = -1
LEADER_BOARD = SortedLinkedList()
POTENTIAL_BOARD = RBTree()
LOCK_RACE = True

LEADER_BOARD.insert(SortedLinkListNode(LeaderBoardObj("h_azarbad77", "https://t.me/c/-1000088202234/295",
                                                      'AgACAgQAAxkBAAIBJ2Eg5rzBSUoOKTbqFgwICUUjiMxCAAIBtTEbJuYIUUo-xujHC2C7ZBZJLl0AAwEAAwIAA3gAA7s-BQABHgQ',
                                                      "C:\\Users\\asus\\Desktop\\Arman\\race_bot\\user_images\\ronaldo\\race_image.jpg",
                                                      12)))
LEADER_BOARD.insert(SortedLinkListNode(LeaderBoardObj("HR_Azarbad", "https://t.me/c/-1000925175130/252",
                                                      "AgACAgQAAxkBAAP8YSDEOnTz3YlFV0BrkEi-4ponqG8AAva1MRvPXAhR8geW3vrqkFddxrUvXQADAQADAgADeQAD88wCAAEeBA",
                                                      "C:\\Users\\asus\\Desktop\\Arman\\race_bot\\user_images\\ronaldo\\race_image.jpg",
                                                      10)))
POTENTIAL_BOARD.insert(RBNode(HasPotentialObj("h_azarbad77", "https://t.me/c/-1000088202234/295",
                                              'AgACAgQAAxkBAAIBJ2Eg5rzBSUoOKTbqFgwICUUjiMxCAAIBtTEbJuYIUUo-xujHC2C7ZBZJLl0AAwEAAwIAA3gAA7s-BQABHgQ',
                                              "C:\\Users\\asus\\Desktop\\Arman\\race_bot\\user_images\\ronaldo\\race_image.jpg",
                                              24)))

NEXT_STATES = {
	"normal_user_initial_state": 0
}

ADMIN_INITIAL_KEYBOARD = ReplyKeyboardMarkup(
	[
		["📣  " + "مشاهده نتایج "],  # First row
		["📷  " + "مشاهده عکس مسابقه "],  # Second row
		["⛳  " + "پایان مسابقه  "],  # Second row
	],
	resize_keyboard=True  # Make the keyboard smaller
)
SUPERVISOR_INITIAL_KEYBOARD = ReplyKeyboardMarkup(
	[
		["📣  " + "مشاهده نتایج "],  # First row
		["📷  " + "مشاهده عکس مسابقه "],  # Second row
		["⛳  " + "ارزیابی عکس‌ها  "],  # Second row
	],
	resize_keyboard=True  # Make the keyboard smaller
)
NORMAL_USER_INITIAL_KEYBOARD = ReplyKeyboardMarkup(
	[
		["📣  " + "مشاهده نتایج "],  # First row
		["📷  " + "مشاهده عکس مسابقه "],  # Second row
		["⛳  " + "ارسال عکس "],  # Second row
	],
	resize_keyboard=True  # Make the keyboard smaller
)


class State(ABC):
	def __init__(self, username: str, client: Client):
		self.username = username
		self.client = client

	@abstractmethod
	def next_state(self):
		pass

	@abstractmethod
	async def default_function(self):
		pass


# Normal user states
class NormalUserLockState(State):
	def next_state(self):
		return NormalUserInitialState(self.username, self.client)

	async def default_function(self):
		await self.client.send_message(
			self.username,
			"هنوز مسابقه جدیدی شروع نشده‌است...",
			reply_markup=ReplyKeyboardRemove()
		)


class NormalUserInitialState(State):
	async def view_leader_board(self, leader_board_number):
		global LEADER_BOARD_MAX_LENGTH
		paginate_keyboard = InlineKeyboard()
		paginate_keyboard.paginate(min(len(LEADER_BOARD), LEADER_BOARD_MAX_LENGTH), leader_board_number,
		                           'leader_board#{number}')
		# paginate_keyboard.row(
		# 	InlineKeyboardButton('Back', 'pagination_keyboard#back'),
		# 	InlineKeyboardButton('Close', 'pagination_keyboard#close')
		# )
		await self.client.send_photo(
			self.username,
			LEADER_BOARD.get_item(leader_board_number).data.media_file_id if min(len(LEADER_BOARD),
			                                                                     LEADER_BOARD_MAX_LENGTH) > leader_board_number - 1 else None,
			f'This is number {leader_board_number}',
			reply_markup=paginate_keyboard
		)

	async def view_race_photo(self):
		await self.client.send_photo(
			self.username,
			RACE_PHOTO_MEDIA_FILE_ID,
			'عکس مسابقه'
		)

	def next_state(self):
		return NormalUserSendingPhotoState(self.username, self.client)

	async def default_function(self):
		await self.client.send_message(
			self.username,
			None,
			reply_markup=ReplyKeyboardMarkup(
				[
					["📣  " + "مشاهده نتایج "],  # First row
					["📷  " + "مشاهده عکس مسابقه "],  # Second row
					["⛳  " + "ارسال عکس "],  # Second row
				],
				resize_keyboard=True  # Make the keyboard smaller
			)
		)


class NormalUserSendingPhotoState(State):
	async def save_user_photo(self, message: Message):
		user_image_file_path = os.path.join(os.getcwd(), "user_images", RACE_PHOTO_FILE, f'{message.chat.username}.jpg')
		await message.download(
			file_name=user_image_file_path
		)
		await self.__check_similarity(message, user_image_file_path)

	def next_state(self):
		return NormalUserInitialState(self.username, self.client)

	async def default_function(self):
		await self.client.send_message(
			self.username,
			"لطفا عکس مورد نظر خود را ارسال کنید..."
		)

	async def __check_similarity(self, message: Message, user_image_file_path: str):
		aipa_response = await AIPA_CLIENT.post_face_verification(user_image_file_path,
		                                                         os.path.join(os.getcwd(), "user_images",
		                                                                      RACE_PHOTO_FILE,
		                                                                      "race_image.jpg"))

		if not str(aipa_response.status_code).startswith('2'):
			await self.client.send_message(
				self.username,
				'متاسفانه مشکلی پیش آمده است. لطفا دوباره امتحان کنید...'
			)
		else:
			similarity = json.loads(aipa_response.content)['similarity']
			if similarity > MINIMUM_SCORE_IN_LEADER_BOARD:
				POTENTIAL_BOARD.insert(RBNode(HasPotentialObj(owner_username=self.username, media_link=message.link,
				                                              media_file_id=message.photo.file_id,
				                                              media_file_path=user_image_file_path, score=similarity,
				                                              migrate_to_persist_db=False)))
				self.client.send_message(
					self.username,
					f'میزان شباهت {similarity} تشخیص داده شده است. عکس شما پتاسیل قرار گرفتن در نفرات برتر را دارد. لطفا منتظر تایید همکاران ما باشد.'
				)
			else:
				self.client.send_message(
					self.username,
					f'میزان شباهت عکس شما، {similarity} تشخیص داده شده‌است... '
				)


# Supervisor states
class SupervisorLockState(State):
	def next_state(self):
		return SupervisorInitialState(self.username, self.client)

	async def default_function(self):
		await self.client.send_message(
			self.username,
			"هنوز مسابقه جدیدی شروع نشده‌است...",
			reply_markup=ReplyKeyboardRemove()
		)


class SupervisorInitialState(NormalUserInitialState):
	async def next_state(self):
		potential_photo = POTENTIAL_BOARD.find_minimum_data()
		if potential_photo is not None:
			POTENTIAL_BOARD.deletion(potential_photo)
			return SupervisorEvaluationState(self.username, self.client, potential_photo.data)
		else:
			await self.client.send_message(
				self.username,
				"عکسی در حال حاضر موجود نیست..."
			)
			return self

	async def default_function(self):
		await self.client.send_message(
			self.username,
			None,
			reply_markup=ReplyKeyboardMarkup(
				[
					["📣  " + "مشاهده نتایج "],  # First row
					["📷  " + "مشاهده عکس مسابقه "],  # Second row
					["⛳  " + "ارزیابی عکس‌ها  "],  # Second row
				],
				resize_keyboard=True  # Make the keyboard smaller
			)
		)


class SupervisorEvaluationState(State):
	def __init__(self, username: str, client: Client, assigned_potential_obj: HasPotentialObj):
		self.assigned_potential_obj = assigned_potential_obj
		super(SupervisorEvaluationState, self).__init__(username, client)

	def next_state(self):
		return SupervisorInitialState(self.username, self.client)

	async def default_function(self):
		await self.client.send_photo(
			self.username,
			self.assigned_potential_obj.media_file_id,
			"This is caption of photo",
			reply_markup=ReplyKeyboardMarkup(
				[
					["📣  " + " تایید"],  # First row
					["📷  " + "رد "],  # Second row
				],
				resize_keyboard=True  # Make the keyboard smaller
			)
		)

	async def confirm_photo(self):
		global MINIMUM_SCORE_IN_LEADER_BOARD
		corresponding_leader_board_obj = HasPotentialObj.convert_to_leader_board_obj(self.assigned_potential_obj)
		if corresponding_leader_board_obj.score > MINIMUM_SCORE_IN_LEADER_BOARD:
			LEADER_BOARD.insert(SortedLinkListNode(corresponding_leader_board_obj))
			MINIMUM_SCORE_IN_LEADER_BOARD = LEADER_BOARD.pruning(LEADER_BOARD_MAX_LENGTH)

		await self.client.send_message(
			self.username,
			"عکس تایید شد..."
		)

	async def reject_photo(self):
		await self.client.send_message(
			self.username,
			"Reject"
		)


# Admin states
class AdminInitialState(NormalUserInitialState):
	def next_state(self):
		return AdminWaitForStartNewRace(self.username, self.client)

	async def default_function(self):
		await self.client.send_message(
			self.username,
			"اگر می‌خواهید مسابقه جدیدی را شروع کنید، ابتدا مسابقه قبلی را خاتمه دهید...",
			reply_markup=ReplyKeyboardMarkup(
				[
					["📣  " + "مشاهده نتایج "],  # First row
					["📷  " + "مشاهده عکس مسابقه "],  # Second row
					["⛳  " + "پایان مسابقه  "],  # Second row
				],
				resize_keyboard=True  # Make the keyboard smaller
			)
		)

	async def finish_race(self, user_states):
		# Set lock_state for all username in user_states
		self.__lock_all_users(user_states)
		# Lock race and prevent to add anything in leader and potential board (set mutex for it?)
		self.__lock_race()
		# Send finish_message for all users and inform them
		await self.__send_finish_message(user_states.keys())
		# Send leader board for all users
		await self.__send_leader_board(user_states.keys())
		# Remove all potential objects
		self.__remove_potential_board()
		# Remove all leader objects
		self.__remove_leader_board()
		# Set Race photo as None
		self.__clean_race_information()
		# save username of user in user_states in DB
		self.__save_username_in_db()
		await self.client.send_message(
			self.username,
			"مسابقه پایان یافت...",
			reply_markup=ReplyKeyboardRemove()
		)

	def __lock_all_users(self, user_states):
		for username in user_states.keys():
			user_states[username] = NormalUserLockState(username, self.client)

		for username in SUPERVISOR_USERS:
			user_states[username] = SupervisorLockState(username, self.client)

	def __lock_race(self):
		global LOCK_RACE
		LOCK_RACE = True

	async def __send_finish_message(self, all_username: list):
		for username in all_username:
			await self.client.send_message(
				username,
				"مسابقه به اتمام رسید و نفرات برتر به شرح زیر می‌باشند...",
				reply_markup=ReplyKeyboardRemove()
			)

	async def __send_leader_board(self, all_username):
		global LEADER_BOARD_MAX_LENGTH
		for index in range(1, min(len(LEADER_BOARD), LEADER_BOARD_MAX_LENGTH) + 1):
			for username in all_username:
				await self.client.send_photo(
					username,
					LEADER_BOARD.get_item(index).data.media_file_id,
					f'This is number {index}'
				)

	def __remove_potential_board(self):
		POTENTIAL_BOARD.deletion_all()

	def __remove_leader_board(self):
		LEADER_BOARD.deletion_all()

	def __clean_race_information(self):
		global RACE_PHOTO_MEDIA_FILE_ID, RACE_PHOTO_MEDIA_LINK
		RACE_PHOTO_MEDIA_FILE_ID = None
		RACE_PHOTO_MEDIA_LINK = None

	def __save_username_in_db(self):
		pass


class AdminWaitForStartNewRace(State):
	def next_state(self):
		return AdminInitialState(self.username, self.client)

	async def default_function(self):
		await self.client.send_message(
			self.username,
			"اگر می‌خواهید مسابقه جدیدی را شروع کنید، کافی است عکسی را ارسال کنید..."
		)

	async def start_new_race(self, user_states: dict, media_link: str, media_file_id: str):
		# Set race information
		self.__set_race_information(media_link, media_file_id)
		# Remove potential board
		self.__remove_potential_board()
		# Remove leader board
		self.__remove_leader_board()
		# Unlock race
		self.__unlock_race()
		# Unlock current users state
		self.__unlock_all_users(user_states)
		# Send start race message for all users
		await self.__send_start_race_message(user_states.keys())

	def __set_race_information(self, media_link: str, media_file_id: str):
		global MINIMUM_SCORE_IN_LEADER_BOARD, RACE_PHOTO_MEDIA_FILE_ID, RACE_PHOTO_MEDIA_LINK
		MINIMUM_SCORE_IN_LEADER_BOARD = -1
		RACE_PHOTO_MEDIA_FILE_ID = media_file_id
		RACE_PHOTO_MEDIA_LINK = media_link

	def __remove_potential_board(self):
		POTENTIAL_BOARD.deletion_all()

	def __remove_leader_board(self):
		LEADER_BOARD.deletion_all()

	def __unlock_race(self):
		global LOCK_RACE
		LOCK_RACE = False

	def __unlock_all_users(self, user_states):
		for username in user_states.keys():
			user_states[username] = NormalUserInitialState(username, self.client)

		for username in SUPERVISOR_USERS:
			user_states[username] = SupervisorInitialState(username, self.client)

	async def __send_start_race_message(self, all_username: list):
		global ADMIN_INITIAL_KEYBOARD, SUPERVISOR_INITIAL_KEYBOARD, NORMAL_USER_INITIAL_KEYBOARD
		for username in all_username:
			if username == ADMIN_USER:
				keyboard = ADMIN_INITIAL_KEYBOARD
			elif username in SUPERVISOR_USERS:
				keyboard = SUPERVISOR_INITIAL_KEYBOARD
			else:
				keyboard = NORMAL_USER_INITIAL_KEYBOARD
			await self.client.send_message(
				username,
				"مسابقه‌ی جدیدی شروع شده‌است....",
				reply_markup=keyboard
			)
