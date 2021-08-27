import json, os
from datetime import datetime
from storage.data import RBTree, SortedLinkedList, SortedLinkListNodeEncoder, RBTreeNodeEncoder
from state.user_state import StateJsonEncoder


class BackupDriver:

	@staticmethod
	def backup_leader_board(leader_board: SortedLinkedList):
		leader_board_list = list(leader_board)
		leader_board_json_file_path = os.path.join(os.getcwd(), 'leader_boards_backup',
		                                           str(datetime.utcnow()).replace(" ", "_").replace(":", "-") + ".json")
		with open(leader_board_json_file_path, mode='w') as backup_file:
			json.dump(leader_board_list, backup_file, cls=SortedLinkListNodeEncoder)

	@staticmethod
	def backup_user_states(user_states_json_file_path: str, user_states: {}):
		print(user_states)
		with open(user_states_json_file_path, mode='w') as backup_file:
			json.dump(user_states, backup_file, cls=StateJsonEncoder)

	@staticmethod
	def backup_potential_board(potential_board: RBTree):
		potential_board_list = list(potential_board)
		potential_board_json_file_path = os.path.join(os.getcwd(), 'potential_boards_backup',
		                                              str(datetime.utcnow()).replace(" ", "_").replace(":",
		                                                                                               "-") + ".json")
		with open(potential_board_json_file_path, mode='w') as backup_file:
			json.dump(potential_board_list, backup_file, cls=RBTreeNodeEncoder)


if __name__ == '__main__':
	pass
	# user_state = {
	# 	"HR_Azarbad": NormalUserInitialState("HR_Azarbad", None),
	# 	"HR_Azarbad2": SupervisorEvaluationState("HR_Azarbad2", None,
	# 	                                         HasPotentialObj("hamidreza", "112", "ldk", "", 12)),
	# }
	# PostgresDriver.backup_user_states(user_state)
	# leader_board = SortedLinkedList()
	# obj1 = SortedLinkListNode(LeaderBoardObj("hamidreza", "112", "ldk", "", 12))
	# obj2 = SortedLinkListNode(LeaderBoardObj("hamidreza", "112", "ldk", "", 13))
	# obj3 = SortedLinkListNode(LeaderBoardObj("hamidreza", "112", "ldk", "", 18))
	# obj4 = SortedLinkListNode(LeaderBoardObj("hamidreza", "112", "ldk", "", 15))
	# obj5 = SortedLinkListNode(LeaderBoardObj("hamidreza", "112", "ldk", "", 19))
	# # print(obj1.data.__dict__)
	# leader_board.insert(obj1)
	# leader_board.insert(obj2)
	# leader_board.insert(obj3)
	# leader_board.insert(obj4)
	# leader_board.insert(obj5)
	# # PostgresDriver.backup_leader_board(leader_board)
	# leader_board = RBTree()
	# obj1 = RBNode(HasPotentialObj("hamidreza", "112", "ldk", "", 12))
	# obj2 = RBNode(HasPotentialObj("hamidreza", "112", "ldk", "", 13))
	# obj3 = RBNode(HasPotentialObj("hamidreza", "112", "ldk", "", 18))
	# obj4 = RBNode(HasPotentialObj("hamidreza", "112", "ldk", "", 15))
	# obj5 = RBNode(HasPotentialObj("hamidreza", "112", "ldk", "", 19))
	# # print(obj1.data.__dict__)
	# leader_board.insert(obj1)
	# leader_board.insert(obj2)
	# leader_board.insert(obj3)
	# leader_board.insert(obj4)
	# leader_board.insert(obj5)
	# PostgresDriver.backup_potential_board(leader_board)