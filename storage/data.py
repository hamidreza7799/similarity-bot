from abc import ABC


class Data(ABC):
	def __init__(self, owner_username, media_link, media_file_id, media_file_path, score, migrate_to_persist_db=False):
		self.owner_username = owner_username
		self.media_link = media_link
		self.media_file_id = media_file_id
		self.media_file_path = media_file_path
		self.score = score
		self.migrate_to_persist_db = migrate_to_persist_db


class HasPotentialObj(Data):
	def __init__(self, owner_username, media_link, media_file_id, media_file_path, score, migrate_to_persist_db=False):
		super(HasPotentialObj, self).__init__(owner_username, media_link, media_file_id, media_file_path, score,
		                                      migrate_to_persist_db)

	@staticmethod
	def convert_to_leader_board_obj(potential_obj: Data):
		return LeaderBoardObj(
			potential_obj.owner_username, potential_obj.media_link, potential_obj.media_file_id,
			potential_obj.media_file_path,
			potential_obj.score
		)


class LeaderBoardObj(Data):
	def __init__(self, owner_username, media_link, media_file_id, media_file_path, score, migrate_to_persist_db=False):
		super(LeaderBoardObj, self).__init__(owner_username, media_link, media_file_id, media_file_path, score,
		                                     migrate_to_persist_db)

	@staticmethod
	def convert_to_potential_obj(leader_board_obj: Data):
		return HasPotentialObj(
			leader_board_obj.owner_username, leader_board_obj.media_link, leader_board_obj.media_file_id,
			leader_board_obj.media_file_path,
			leader_board_obj.score
		)


# Red Black tree Node
class RBNode:
	def __init__(self, data: Data):
		self.red = False
		self.parent = None
		self.data = data  # data is HasPotentialObj or LeaderBoardObj
		self.left = None
		self.right = None


# Red Black tree
class RBTree:
	def __init__(self):
		self.nil = RBNode(LeaderBoardObj("", "", "", "", False))
		self.nil.red = False
		self.nil.left = None
		self.nil.right = None
		self.root = self.nil
		self.length = 0

	@staticmethod
	def pre_order(current_node: RBNode, nil: RBNode):
		if current_node is nil:
			return []
		return RBTree.pre_order(current_node.left, nil) + [current_node.data] + RBTree.pre_order(
			current_node.right, nil)

	def find_minimum_data(self):
		if self.root is self.nil:
			return
		current = self.root
		while current.left is not self.nil:
			current = current.left
		return current

	def find_minimum_data_in_sub_tree(self, data: Data):
		if data is self.nil:
			return
		current = data
		while current.left is not self.nil:
			current = current.left
		return current

	def find_data(self, data: Data):
		current = self.root
		while current is not self.nil and data.score != current.data.score:
			if data.score < current.data.score:
				current = current.left
			else:
				current = current.right
		return current

	def deletion_all(self):
		self.root = self.nil
		self.length = 0

	# Node deletion
	def deletion(self, node: RBNode):
		custom_node = self.find_data(node.data)
		if custom_node is self.nil:
			print("Cannot find key in the tree")
			return
		original_color_is_black = not custom_node.red
		if custom_node.left == self.nil:
			x = custom_node.right
			self.__rb_transplant(custom_node, custom_node.right)
		elif custom_node.right is self.nil:
			x = custom_node.left
			self.__rb_transplant(custom_node, custom_node.left)
		else:
			y = self.find_minimum_data_in_sub_tree(custom_node.right)
			original_color_is_black = not y.red
			x = y.right
			if y.parent == custom_node:
				x.parent = y
			else:
				self.__rb_transplant(y, y.right)
				y.right = custom_node.right
				y.right.parent = y

			self.__rb_transplant(custom_node, y)
			y.left = custom_node.left
			y.left.parent = y
			y.red = custom_node.red
		if original_color_is_black:
			self.__delete_fix(x)
		self.length -= 1

	def __delete_fix(self, data: Data):
		while data != self.root and not data.red:
			if data == data.parent.left:
				uncle = data.parent.right
				if uncle.red:
					uncle.red = False
					uncle.parent.red = True
					self.__rotate_left(data.parent)
					uncle = data.parent.right

				if not uncle.left.red and not uncle.right.red:
					uncle.red = True
					data = data.parent
				else:
					if not uncle.right.red:
						uncle.left.red = False
						uncle.red = True
						self.__rotate_right(uncle)
						uncle = data.parent.right

					uncle.red = data.parent.red
					data.parent.red = False
					uncle.right.red = False
					self.__rotate_left(data.parent)
					data = self.root
			else:
				uncle = data.parent.left
				if uncle.red:
					uncle.red = False
					data.parent.red = True
					self.__rotate_right(data.parent)
					uncle = data.parent.left

				if not uncle.right.red and not uncle.left.red:
					uncle.red = True
					data = data.parent
				else:
					if not uncle.left.red:
						uncle.right.red = False
						uncle.red = True
						self.__rotate_left(uncle)
						uncle = data.parent.left

					uncle.red = data.parent.red
					data.parent.red = False
					uncle.left.red = False
					self.__rotate_right(data.parent)
					data = self.root
		data.red = False

	def insert(self, new_node: RBNode):
		# Ordinary Binary Search Insertion
		new_node.parent = None
		new_node.left = self.nil
		new_node.right = self.nil
		new_node.red = True  # new node must be red

		parent = None
		current = self.root
		while current != self.nil:
			parent = current
			if new_node.data.score < current.data.score:
				current = current.left
			else:
				current = current.right

		# Set the parent and insert the new node
		new_node.parent = parent
		if parent is None:
			self.root = new_node
		elif new_node.data.score < parent.data.score:
			parent.left = new_node
		else:
			parent.right = new_node

		self.length += 1
		# Fix the tree
		self.__fix_insert(new_node)

	def __fix_insert(self, new_node: RBNode):
		while new_node != self.root and new_node.parent.red:
			if new_node.parent == new_node.parent.parent.right:
				u = new_node.parent.parent.left  # uncle
				if u.red:
					u.red = False
					new_node.parent.red = False
					new_node.parent.parent.red = True
					new_node = new_node.parent.parent
				else:
					if new_node == new_node.parent.left:
						new_node = new_node.parent
						self.__rotate_right(new_node)
					new_node.parent.red = False
					new_node.parent.parent.red = True
					self.__rotate_left(new_node.parent.parent)
			else:
				u = new_node.parent.parent.right  # uncle

				if u.red:
					u.red = False
					new_node.parent.red = False
					new_node.parent.parent.red = True
					new_node = new_node.parent.parent
				else:
					if new_node == new_node.parent.right:
						new_node = new_node.parent
						self.__rotate_left(new_node)
					new_node.parent.red = False
					new_node.parent.parent.red = True
					self.__rotate_right(new_node.parent.parent)
		self.root.red = False

	# rotate left at node x
	def __rotate_left(self, x):
		y = x.right
		x.right = y.left
		if y.left != self.nil:
			y.left.parent = x

		y.parent = x.parent
		if x.parent is None:
			self.root = y
		elif x == x.parent.left:
			x.parent.left = y
		else:
			x.parent.right = y
		y.left = x
		x.parent = y

	# rotate right at node x
	def __rotate_right(self, x):
		y = x.left
		x.left = y.right
		if y.right != self.nil:
			y.right.parent = x

		y.parent = x.parent
		if x.parent is None:
			self.root = y
		elif x == x.parent.right:
			x.parent.right = y
		else:
			x.parent.left = y
		y.right = x
		x.parent = y

	# Transplant two node with (replace u with v)
	def __rb_transplant(self, u: RBNode, v: RBNode):
		if u.parent is None:
			self.root = v
		elif u is u.parent.left:
			u.parent.left = v
		else:
			u.parent.right = v
		v.parent = u.parent


# Sorted link list Node
class SortedLinkListNode:
	def __init__(self, data: LeaderBoardObj):
		self.data = data
		self.next = None


# Sorted Link List Data Structure
class SortedLinkedList:
	def __init__(self):
		self.head = None

	def insert(self, new_node: SortedLinkListNode):
		if self.head is None:
			self.head = new_node
		elif self.head.data.score < new_node.data.score:
			new_node.next = self.head
			self.head = new_node
		else:
			current = self.head
			while (current.next is not None and
			       current.next.data.score >= new_node.data.score):
				current = current.next

			new_node.next = current.next
			current.next = new_node

	def pruning(self, max_length: int) -> None:
		current = self.head
		while max_length > 1:
			if current is None:
				return
			current = current.next
			max_length -= 1

		if current is not None:
			current.next = None
			return

	def find_minimum_item(self) -> SortedLinkListNode:
		current = self.head
		while current is not None:
			if current.next is not None:
				current = current.next
			else:
				return current

	def get_item(self, index: int):
		current = self.head
		while index > 1 and current is not None:
			current = current.next
			index -= 1
		if index == 1:
			return current
		else:
			return None

	def deletion_all(self):
		self.head = None

	def __str__(self):
		result = []
		temp = self.head
		while temp is not None:
			result += [str(temp.data.score)]
			temp = temp.next
		return ",".join(result)

	def __len__(self):
		len = 0
		current = self.head
		while current is not None:
			len += 1
			current = current.next
		return len


def migrate_data_to_db():
	pass


if __name__ == "__main__":
	# leader_board = RBTree()
	# obj1 = RBNode(LeaderBoardObj("hamidreza", "112", "ldk", 12))
	# obj2 = RBNode(LeaderBoardObj("hamidreza", "112", "ldk", 13))
	# obj3 = RBNode(LeaderBoardObj("hamidreza", "112", "ldk", 14))
	# obj4 = RBNode(LeaderBoardObj("hamidreza", "112", "ldk", 15))
	# obj5 = RBNode(LeaderBoardObj("hamidreza", "112", "ldk", 16))
	# leader_board.insert(obj1)
	# leader_board.insert(obj2)
	# leader_board.insert(obj3)
	# leader_board.insert(obj4)
	# leader_board.insert(obj5)
	# print(RBTree.pre_order(leader_board.root, leader_board.nil))
	# leader_board.deletion(obj2)
	# print(RBTree.pre_order(leader_board.root, leader_board.nil))
	leader_board = SortedLinkedList()
	obj1 = SortedLinkListNode(LeaderBoardObj("hamidreza", "112", "ldk", 12))
	obj2 = SortedLinkListNode(LeaderBoardObj("hamidreza", "112", "ldk", 13))
	obj3 = SortedLinkListNode(LeaderBoardObj("hamidreza", "112", "ldk", 18))
	obj4 = SortedLinkListNode(LeaderBoardObj("hamidreza", "112", "ldk", 15))
	obj5 = SortedLinkListNode(LeaderBoardObj("hamidreza", "112", "ldk", 19))
	leader_board.insert(obj1)
	leader_board.insert(obj2)
	leader_board.insert(obj3)
	leader_board.insert(obj4)
	leader_board.insert(obj5)
	print(leader_board)
	a = leader_board.pruning(5)
	print(leader_board, a)
	print(leader_board.get_item(2).data.score)
	print(len(leader_board))
