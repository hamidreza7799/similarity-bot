from datetime import datetime
from pykeyboard import InlineKeyboard
from pyrogram import Client
from pyrogram.types import Message
from pyrogram.types import ReplyKeyboardRemove
from abc import abstractmethod
from aipa.aipa import *
from race_config import NORMAL_USER_INITIAL_KEYBOARD, SUPERVISOR_INITIAL_KEYBOARD, ADMIN_INITIAL_KEYBOARD, ADMIN_USER, \
	SUPERVISOR_USERS, SUPERVISOR_EVALUATION_KEYBOARD, NORMAL_USER_SENDING_PHOTO_KEYBOARD, BACKUP_MINUTES
from storage.data import *
import threading

AIPA_CLIENT = AipaRestClient()
AIPA_CLIENT.get_valid_access_token()
RACE_PHOTO_MEDIA_LINK = "https://t.me/c/-1000925175130/252"
RACE_PHOTO_MEDIA_FILE_ID = "AgACAgQAAxkBAAP8YSDEOnTz3YlFV0BrkEi-4ponqG8AAva1MRvPXAhR8geW3vrqkFddxrUvXQADAQADAgADeQAD88wCAAEeBA"
RACE_PHOTO_FILE = "ronaldo"
LEADER_BOARD_MAX_LENGTH = 10
MINIMUM_SCORE_IN_LEADER_BOARD = -1
LEADER_BOARD = SortedLinkedList()
POTENTIAL_BOARD = RBTree()

LEADER_BOARD.insert(SortedLinkListNode(LeaderBoardObj(1, "https://t.me/c/-1000088202234/295",
                                                      'AgACAgQAAxkBAAIBJ2Eg5rzBSUoOKTbqFgwICUUjiMxCAAIBtTEbJuYIUUo-xujHC2C7ZBZJLl0AAwEAAwIAA3gAA7s-BQABHgQ',
                                                      "C:\\Users\\asus\\Desktop\\Arman\\similarity_race_bot\\user_images\\ronaldo\\race_image.jpg",
                                                      12)))
LEADER_BOARD.insert(SortedLinkListNode(LeaderBoardObj(2, "https://t.me/c/-1000925175130/252",
                                                      "AgACAgQAAxkBAAP8YSDEOnTz3YlFV0BrkEi-4ponqG8AAva1MRvPXAhR8geW3vrqkFddxrUvXQADAQADAgADeQAD88wCAAEeBA",
                                                      "C:\\Users\\asus\\Desktop\\Arman\\similarity_race_bot\\user_images\\ronaldo\\race_image.jpg",
                                                      10)))
POTENTIAL_BOARD.insert(RBNode(HasPotentialObj(3, "https://t.me/c/-1000088202234/295",
                                              'AgACAgQAAxkBAAIBJ2Eg5rzBSUoOKTbqFgwICUUjiMxCAAIBtTEbJuYIUUo-xujHC2C7ZBZJLl0AAwEAAwIAA3gAA7s-BQABHgQ',
                                              "C:\\Users\\asus\\Desktop\\Arman\\similarity_race_bot\\user_images\\ronaldo\\race_image.jpg",
                                              24)))
POTENTIAL_BOARD.insert(RBNode(HasPotentialObj(4, "https://t.me/c/-1000088202234/295",
                                              'AgACAgQAAxkBAAIBJ2Eg5rzBSUoOKTbqFgwICUUjiMxCAAIBtTEbJuYIUUo-xujHC2C7ZBZJLl0AAwEAAwIAA3gAA7s-BQABHgQ',
                                              "C:\\Users\\asus\\Desktop\\Arman\\similarity_race_bot\\user_images\\ronaldo\\race_image.jpg",
                                              24)))


class State(ABC):
	def __init__(self, user_id: int, client: Client = None):
		self.__user_id = user_id
		self.__client = client

	@property
	def user_id(self):
		return self.__user_id

	@property
	def client(self):
		return self.__client

	@abstractmethod
	def next_state(self):
		pass

	@abstractmethod
	async def default_function(self):
		pass

	@abstractmethod
	def back_state(self):
		pass

	@abstractmethod
	def json_serializer(self):
		pass


# Normal user states
class NormalUserLockState(State):
	def next_state(self):
		return NormalUserInitialState(self.user_id, self.client)

	async def default_function(self):
		await self.client.send_message(
			self.user_id,
			"هنوز مسابقه جدیدی شروع نشده‌است...",
			reply_markup=ReplyKeyboardRemove()
		)

	def back_state(self):
		return self

	def json_serializer(self):
		return {"class_type": self.__class__}


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
		leader_board_obj = LEADER_BOARD.get_item(leader_board_number) if min(len(LEADER_BOARD),
		                                                                     LEADER_BOARD_MAX_LENGTH) > leader_board_number - 1 else None
		if leader_board_obj is None:
			await self.client.send_message(
				self.user_id,
				'فعلا چیزی برای نمایش وجود ندارد...'
			)
		else:
			await self.client.send_photo(
				self.user_id,
				leader_board_obj.data.media_file_id,
				f'رتبه‌ی {leader_board_number} با امتیاز {leader_board_obj.data.score}',
				reply_markup=paginate_keyboard
			)

	async def view_race_photo(self):
		await self.client.send_photo(
			self.user_id,
			RACE_PHOTO_MEDIA_FILE_ID,
			'عکس مسابقه'
		)

	def next_state(self):
		return NormalUserSendingPhotoState(self.user_id, self.client)

	async def default_function(self):
		await self.client.send_message(
			self.user_id,
			"شما کارهای زیر می‌توانید انجام دهید...",
			reply_markup=NORMAL_USER_INITIAL_KEYBOARD
		)

	def back_state(self):
		return self

	def json_serializer(self):
		return {"class_type": str(self.__class__)}


class NormalUserSendingPhotoState(State):
	def save_user_photo(self):
		return NormalUserWaitForAIPAResult(self.user_id, self.client)

	def next_state(self):
		return NormalUserInitialState(self.user_id, self.client)

	async def default_function(self):
		await self.client.send_message(
			self.user_id,
			"لطفا عکس مورد نظر خود را ارسال کنید...",
			reply_markup=NORMAL_USER_SENDING_PHOTO_KEYBOARD
		)

	def back_state(self):
		return NormalUserInitialState(self.user_id, self.client)

	def json_serializer(self):
		return {"class_type": str(self.__class__)}


class NormalUserWaitForAIPAResult(State):
	def next_state(self):
		return NormalUserInitialState(self.user_id, self.client)

	def back_state(self):
		return self

	async def work_with_aipa(self, message: Message):
		user_image_file_path = os.path.join(os.getcwd(), "user_images",
		                                    RACE_PHOTO_FILE,
		                                    f'{message.chat.username if message.chat.username is not None else str(message.chat.id)}.jpg')
		await message.download(
			file_name=user_image_file_path
		)
		await self.default_function()
		await self.__check_similarity(message, user_image_file_path)

	async def default_function(self):
		await self.client.send_message(
			self.user_id,
			'مدل در حال بررسی میزان شباهت می‌باشد. منتظر باشید...'
		)

	async def __check_similarity(self, message: Message, user_image_file_path: str):
		aipa_response = await AIPA_CLIENT.post_face_verification(user_image_file_path,
		                                                         os.path.join(os.getcwd(),
		                                                                      "user_images",
		                                                                      RACE_PHOTO_FILE,
		                                                                      "race_image.jpg"))

		if not str(aipa_response.status_code).startswith('2'):
			await self.client.send_message(
				self.user_id,
				'متاسفانه مشکلی پیش آمده است. لطفا دوباره امتحان کنید...'
			)
		else:
			aipa_response_content = json.loads(aipa_response.content)
			similarity = aipa_response_content['similarity'] if 'similarity' in aipa_response_content else -1
			if similarity == -1:
				await self.client.send_message(
					self.user_id,
					'تصویر ارسالی مشکل دارد. لطفا دوباره امتحان کنید...'
				)
			elif similarity > MINIMUM_SCORE_IN_LEADER_BOARD:
				POTENTIAL_BOARD.insert(RBNode(HasPotentialObj(owner_user_id=self.user_id, media_link=message.link,
				                                              media_file_id=message.photo.file_id,
				                                              media_file_path=user_image_file_path, score=similarity,
				                                              migrate_to_persist_db=False)))
				await self.client.send_message(
					self.user_id,
					f'میزان شباهت {similarity} تشخیص داده شده است. عکس شما پتاسیل قرار گرفتن در نفرات برتر را دارد. لطفا منتظر تایید همکاران ما باشد.'
				)
			else:
				await self.client.send_message(
					self.user_id,
					f'میزان شباهت عکس شما، {similarity} تشخیص داده شده‌است... '
				)

	def json_serializer(self):
		return {"class_type": str(self.__class__)}


# Supervisor states
class SupervisorLockState(State):
	def next_state(self):
		return SupervisorInitialState(self.user_id, self.client)

	def back_state(self):
		return self

	async def default_function(self):
		await self.client.send_message(
			self.user_id,
			"هنوز مسابقه جدیدی شروع نشده‌است...",
			reply_markup=ReplyKeyboardRemove()
		)

	def json_serializer(self):
		return {"class_type": str(self.__class__)}


class SupervisorInitialState(NormalUserInitialState):
	async def next_state(self):
		potential_photo = POTENTIAL_BOARD.find_minimum_data()
		if potential_photo is not None:
			POTENTIAL_BOARD.deletion(potential_photo)
			return SupervisorEvaluationState(self.user_id, self.client, potential_photo.data, POTENTIAL_BOARD.length)
		else:
			await self.client.send_message(
				self.user_id,
				"عکسی در حال حاضر موجود نیست..."
			)
			return self

	def back_state(self):
		return self

	async def default_function(self):
		await self.client.send_message(
			self.user_id,
			"شما کارهای زیر می‌توانید انجام دهید...",
			reply_markup=SUPERVISOR_INITIAL_KEYBOARD
		)


class SupervisorEvaluationState(State):
	def __init__(self, user_id: int, client: Client, assigned_potential_obj: HasPotentialObj,
	             potential_board_length: int):
		self.assigned_potential_obj = assigned_potential_obj
		self.potential_board_length = potential_board_length
		super(SupervisorEvaluationState, self).__init__(user_id, client)

	async def next_state(self):
		potential_photo = POTENTIAL_BOARD.find_minimum_data()
		if potential_photo is not None:
			POTENTIAL_BOARD.deletion(potential_photo)
			return SupervisorEvaluationState(self.user_id, self.client, potential_photo.data, POTENTIAL_BOARD.length)
		else:
			await self.client.send_message(
				self.user_id,
				"عکسی در حال حاضر موجود نیست..."
			)
			return SupervisorInitialState(self.user_id, self.client)

	def back_state(self):
		POTENTIAL_BOARD.insert(RBNode(self.assigned_potential_obj))
		return SupervisorInitialState(self.user_id, self.client)

	async def default_function(self):
		await self.client.send_photo(
			self.user_id,
			self.assigned_potential_obj.media_file_id,
			f'عکسی که باید ارزیابی کنید. تعداد {self.potential_board_length} باقی است...',
			reply_markup=SUPERVISOR_EVALUATION_KEYBOARD
		)

	async def confirm_photo(self):
		global MINIMUM_SCORE_IN_LEADER_BOARD
		corresponding_leader_board_obj = HasPotentialObj.convert_to_leader_board_obj(self.assigned_potential_obj)
		if corresponding_leader_board_obj.score > MINIMUM_SCORE_IN_LEADER_BOARD:
			LEADER_BOARD.insert(SortedLinkListNode(corresponding_leader_board_obj))
			leader_board_minimum_item = LEADER_BOARD.find_minimum_item()
			if leader_board_minimum_item is not None:
				MINIMUM_SCORE_IN_LEADER_BOARD = leader_board_minimum_item.data.score

		await self.client.send_message(
			self.user_id,
			"عکس تایید شد..."
		)

	async def reject_photo(self):
		await self.client.send_message(
			self.user_id,
			"Reject"
		)

	def json_serializer(self):
		return {"class_type": str(self.__class__), "assign_obj": self.assigned_potential_obj.json_serializer()}


# Admin states
class AdminInitialState(NormalUserInitialState):
	def next_state(self):
		return AdminWaitForStartNewRace(self.user_id, self.client)

	def back_state(self):
		return self

	async def default_function(self):
		await self.client.send_message(
			self.user_id,
			"اگر می‌خواهید مسابقه جدیدی را شروع کنید، ابتدا مسابقه قبلی را خاتمه دهید...",
			reply_markup=ADMIN_INITIAL_KEYBOARD
		)

	async def finish_race(self, user_states: {}):
		# Set lock_state for all user_id in user_states
		self.__lock_all_users(user_states)
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
		# save user_id of user in user_states in DB
		self.__save_user_id_in_db()
		await self.client.send_message(
			self.user_id,
			"مسابقه پایان یافت...",
			reply_markup=ReplyKeyboardRemove()
		)

	def __lock_all_users(self, user_states: {}):
		for user_id in user_states.keys():
			user_states[user_id] = NormalUserLockState(user_id, self.client)

		for user_id in SUPERVISOR_USERS:
			user_states[user_id] = SupervisorLockState(user_id, self.client)

	def __lock_race(self):
		global LOCK_RACE
		LOCK_RACE = True

	async def __send_finish_message(self, all_user_id: list):
		for user_id in all_user_id:
			await self.client.send_message(
				user_id,
				"مسابقه به اتمام رسید و نفرات برتر به شرح زیر می‌باشند...",
				reply_markup=ReplyKeyboardRemove()
			)

	async def __send_leader_board(self, all_user_id):
		global LEADER_BOARD_MAX_LENGTH
		for index in range(1, min(len(LEADER_BOARD), LEADER_BOARD_MAX_LENGTH) + 1):
			leader_board_obj = LEADER_BOARD.get_item(index)
			for user_id in all_user_id:
				await self.client.send_photo(
					user_id,
					leader_board_obj.data.media_file_id,
					f'رتبه‌ی {index} با امتیاز {leader_board_obj.data.score}',
				)

	def __remove_potential_board(self):
		POTENTIAL_BOARD.deletion_all()

	def __remove_leader_board(self):
		LEADER_BOARD.deletion_all()

	def __clean_race_information(self):
		global RACE_PHOTO_MEDIA_FILE_ID, RACE_PHOTO_MEDIA_LINK, RACE_PHOTO_FILE
		RACE_PHOTO_MEDIA_FILE_ID = None
		RACE_PHOTO_MEDIA_LINK = None
		RACE_PHOTO_FILE = None

	def __save_user_id_in_db(self):
		pass


class AdminWaitForStartNewRace(State):
	def next_state(self):
		return AdminInitialState(self.user_id, self.client)

	def back_state(self):
		return self

	async def default_function(self):
		await self.client.send_message(
			self.user_id,
			"اگر می‌خواهید مسابقه جدیدی را شروع کنید، کافی است عکسی را ارسال کنید..."
		)

	async def start_new_race(self, user_states: {}, message: Message):
		# Set race information
		self.__set_race_information(message)
		# Remove potential board
		self.__remove_potential_board()
		# Remove leader board
		self.__remove_leader_board()
		# Unlock current users state
		self.__unlock_all_users(user_states)
		# Send start race message for all users
		await self.__send_start_race_message(user_states.keys())

	def __set_race_information(self, message: Message):
		global MINIMUM_SCORE_IN_LEADER_BOARD, RACE_PHOTO_MEDIA_FILE_ID, RACE_PHOTO_MEDIA_LINK, RACE_PHOTO_FILE
		MINIMUM_SCORE_IN_LEADER_BOARD = -1
		RACE_PHOTO_MEDIA_FILE_ID = message.photo.file_id
		RACE_PHOTO_MEDIA_LINK = message.link
		RACE_PHOTO_FILE = str(datetime.utcnow()).split('.')[0].replace(" ", "_").replace(":", "-")
		if not os.path.exists(os.path.join(os.getcwd(), "user_images",
		                                   RACE_PHOTO_FILE)):
			os.mkdir(os.path.join(os.getcwd(), "user_images",
			                      RACE_PHOTO_FILE))
		race_image_file_path = os.path.join(os.getcwd(), "user_images",
		                                    RACE_PHOTO_FILE, f'race_image.jpg')
		loop = asyncio.get_event_loop()
		loop.create_task(message.download(file_name=race_image_file_path))

	def __remove_potential_board(self):
		POTENTIAL_BOARD.deletion_all()

	def __remove_leader_board(self):
		LEADER_BOARD.deletion_all()

	def __unlock_race(self):
		LOCK_RACE = False

	def __unlock_all_users(self, user_states: {}):
		for user_id in user_states.keys():
			user_states[user_id] = NormalUserInitialState(user_id, self.client)

		for user_id in SUPERVISOR_USERS:
			user_states[user_id] = SupervisorInitialState(user_id, self.client)

	async def __send_start_race_message(self, all_user_id: list):
		for user_id in all_user_id:
			if user_id == ADMIN_USER:
				keyboard = ADMIN_INITIAL_KEYBOARD
			elif user_id in SUPERVISOR_USERS:
				keyboard = SUPERVISOR_INITIAL_KEYBOARD
			else:
				keyboard = NORMAL_USER_INITIAL_KEYBOARD
			await self.client.send_message(
				user_id,
				"مسابقه‌ی جدیدی شروع شده‌است....",
				reply_markup=keyboard
			)

	def json_serializer(self):
		return {"class_type": str(self.__class__)}


from storage.backup import BackupDriver


def backup_potential_board():
	global RACE_PHOTO_FILE
	if RACE_PHOTO_FILE is not None:
		potential_board_json_file_path = os.path.join(os.getcwd(), 'backup', "potential_boards",
		                                              RACE_PHOTO_FILE + ".json")
		BackupDriver.backup_potential_board(potential_board_json_file_path, POTENTIAL_BOARD)
	threading.Timer(BACKUP_MINUTES * 60, backup_potential_board).start()


def backup_leader_board():
	global RACE_PHOTO_FILE
	if RACE_PHOTO_FILE is not None:
		leader_board_json_file_path = os.path.join(os.getcwd(), 'backup', "leader_boards", RACE_PHOTO_FILE + ".json")
		BackupDriver.backup_leader_board(leader_board_json_file_path, LEADER_BOARD)
	threading.Timer(BACKUP_MINUTES * 60, backup_leader_board).start()


threading.Timer(BACKUP_MINUTES * 60, backup_potential_board).start()
threading.Timer(BACKUP_MINUTES * 60, backup_leader_board).start()
