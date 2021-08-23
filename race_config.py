from configparser import ConfigParser
import os

RACE_PHOTO_MEDIA_LINK = "https://t.me/c/-1000925175130/252"
RACE_PHOTO_MEDIA_FILE_ID = "AgACAgQAAxkBAAP8YSDEOnTz3YlFV0BrkEi-4ponqG8AAva1MRvPXAhR8geW3vrqkFddxrUvXQADAQADAgADeQAD88wCAAEeBA"
RACE_PHOTO_NAME = "Ronaldo"
LEADER_BOARD_MAX_LENGTH = 10
MINIMUM_SCORE_IN_LEADER_BOARD = -1
LEADER_BOARD = SortedLinkedList()
POTENTIAL_BOARD = RBTree()
LOCK_RACE = True

LEADER_BOARD.insert(SortedLinkListNode(LeaderBoardObj("h_azarbad77", "https://t.me/c/-1000088202234/295",
                                                      'AgACAgQAAxkBAAIBJ2Eg5rzBSUoOKTbqFgwICUUjiMxCAAIBtTEbJuYIUUo-xujHC2C7ZBZJLl0AAwEAAwIAA3gAA7s-BQABHgQ',
                                                      12)))
LEADER_BOARD.insert(SortedLinkListNode(LeaderBoardObj("HR_Azarbad", "https://t.me/c/-1000925175130/252",
                                                      "AgACAgQAAxkBAAP8YSDEOnTz3YlFV0BrkEi-4ponqG8AAva1MRvPXAhR8geW3vrqkFddxrUvXQADAQADAgADeQAD88wCAAEeBA",
                                                      10)))
POTENTIAL_BOARD.insert(RBNode(HasPotentialObj("h_azarbad77", "https://t.me/c/-1000088202234/295",
                                              'AgACAgQAAxkBAAIBJ2Eg5rzBSUoOKTbqFgwICUUjiMxCAAIBtTEbJuYIUUo-xujHC2C7ZBZJLl0AAwEAAwIAA3gAA7s-BQABHgQ',
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


config = ConfigParser()
config_path = os.path.join(os.getcwd(), 'bot_config.ini')
if not os.path.isfile(config_path):
	raise BadConfigError
config.read(config_path)
bot_token = config.get('race_bot', 'bot_token')
api_id = config.get('race_bot', 'api_id')
api_hash = config.get('race_bot', 'api_hash')
ADMIN_USER = "h_azarbad77"
SUPERVISOR_USERS = ["vahidsavabieh"]



