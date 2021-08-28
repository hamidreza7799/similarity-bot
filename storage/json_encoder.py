from json import JSONEncoder
from state.user_state import State
from storage.data import RBNode, SortedLinkListNode


class StateJsonEncoder(JSONEncoder):
	def default(self, o: State):
		return o.json_serializer()


class RBTreeNodeEncoder(JSONEncoder):
	def default(self, o: RBNode):
		return o.data.json_serializer()


class SortedLinkListNodeEncoder(JSONEncoder):
	def default(self, o: SortedLinkListNode):
		return o.data.json_serializer()
