from configparser import ConfigParser
import os


class PostgresDriver:

	def __get_db_setting(self):
		config = ConfigParser()
		config_path = os.path.join(os.path.join(
			os.path.normpath(os.getcwd() + os.sep + os.pardir), 'config', 'database.ini'))
		if not os.path.isfile(config_path):
			raise Exception()
		config.read(config_path)
		bot_token = config.get('race_bot', 'bot_token')
		api_id = config.get('race_bot', 'api_id')
		api_hash = config.get('race_bot', 'api_hash')
