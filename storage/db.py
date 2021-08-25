from configparser import ConfigParser
from storage.data import *
from datetime import datetime
import os, json
import psycopg2


class PostgresDriver:
	__host: str
	__user: str
	__password: str
	__database: str

	def __init__(self):
		self.__host = ""
		self.__user = ""
		self.__password = ""
		self.__database = ""

	@staticmethod
	def backup_leader_board(leader_board: SortedLinkedList):
		leader_board_list = list(leader_board)
		leader_board_json_file_path = os.path.join(os.getcwd(), 'leader_boards_backup',
		                                           str(datetime.utcnow()).replace(" ", "_").replace(":", "-") + ".json")
		with open(leader_board_json_file_path, mode='w') as backup_file:
			json.dump(leader_board_list, backup_file)

	def migrate_and_backup_user_states(self):
		pass

	def migrate_and_backup_potential_board(self):
		pass

	def __connect(self):
		""" Connect to the PostgreSQL database server """
		conn = None
		try:
			# read connection parameters
			self.__get_db_setting()

			# connect to the PostgreSQL server
			print('Connecting to the PostgreSQL database...')
			conn = psycopg2.connect(
				**{"host": self.host, "user": self.user, "password": self.password, "database": self.database})

			# create a cursor
			cur = conn.cursor()

			# execute a statement
			print('PostgreSQL database version:')
			cur.execute('SELECT version()')

			# display the PostgreSQL database server version
			db_version = cur.fetchone()
			print(db_version)

			# close the communication with the PostgreSQL
			cur.close()
		except (Exception, psycopg2.DatabaseError) as error:
			print(error)
		finally:
			if conn is not None:
				conn.close()
				print('Database connection closed.')

	def __get_db_setting(self):
		config = ConfigParser()
		config_path = os.path.join(os.path.join(
			os.path.normpath(os.getcwd() + os.sep + os.pardir), 'config', 'database.ini'))
		if not os.path.isfile(config_path):
			raise Exception()
		config.read(config_path)
		self.host = config.get('postgresql', 'host')
		self.database = config.get('postgresql', 'database')
		self.user = config.get('postgresql', 'user')
		self.password = config.get('postgresql', 'password')

	@property
	def host(self):
		return self.__host

	@host.setter
	def host(self, host: str):
		self.__host = host

	@property
	def user(self):
		return self.__user

	@user.setter
	def user(self, user: str):
		self.__user = user

	@property
	def password(self):
		return self.__password

	@password.setter
	def password(self, password: str):
		self.__password = password

	@property
	def database(self):
		return self.__database

	@database.setter
	def database(self, database: str):
		self.__database = database


if __name__ == '__main__':
	# driver = PostgresDriver()
	leader_board = SortedLinkedList()
	obj1 = SortedLinkListNode(LeaderBoardObj("hamidreza", "112", "ldk", "", 12))
	obj2 = SortedLinkListNode(LeaderBoardObj("hamidreza", "112", "ldk", "", 13))
	obj3 = SortedLinkListNode(LeaderBoardObj("hamidreza", "112", "ldk", "", 18))
	obj4 = SortedLinkListNode(LeaderBoardObj("hamidreza", "112", "ldk", "", 15))
	obj5 = SortedLinkListNode(LeaderBoardObj("hamidreza", "112", "ldk", "", 19))
	#print(LeaderBoardObj("hamidreza", "112", "ldk", "", 12).__dict__)
	leader_board.insert(obj1)
	leader_board.insert(obj2)
	leader_board.insert(obj3)
	leader_board.insert(obj4)
	leader_board.insert(obj5)
	#print(obj1.__dict__)
	PostgresDriver.backup_leader_board(leader_board)
