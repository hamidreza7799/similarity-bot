from configparser import ConfigParser
import os

from pyrogram import filters
from pyrogram.types import ReplyKeyboardMarkup

ADMIN_USER = None
SUPERVISOR_USERS = ["HR_Azarbad"]

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

photo_from_admin_user_filter = filters.create(lambda _, __, query: query.from_user.username == ADMIN_USER)

config = ConfigParser()
config_path = os.path.join(os.getcwd(), 'bot_config.ini')
print(config_path)
if not os.path.isfile(config_path):
	raise Exception()
config.read(config_path)
bot_token = config.get('race_bot', 'bot_token')
api_id = config.get('race_bot', 'api_id')
api_hash = config.get('race_bot', 'api_hash')
