# NODES

# Node to construct pieces
class BasicNode:
	def __init__(self, value):
		self.value = value
		self.connected = None
		
# Node for construct queue buff structure
class SimpleNode:
	def __init__(self, data):
		self.data = data
		self.next = None

# Node for construct linked list bidirectional
class BidirectionalNode:
	def __init__(self, data=None):
		self.data = data
		self.left = None
		self.right = None
		
class QuadirectionalNode(BidirectionalNode):
	def __init__(self, data=None):
		BidirectionalNode.__init__(self, data)
		self.down = None
		self.high = None
		
# Node for gameboard structure
class PolydirectionalNode(QuadirectionalNode):
	def __init__(self, data=None):
		QuadirectionalNode.__init__(self, data)
		self.lddiag = None
		self.rddiag = None
		self.lhdiag = None
		self.rhdiag = None

# ORIENTATIONS
# Functions to advanced in the nodes orientations

class BidirectionalOrientations:
	lnode = lambda unknow, node: node.left
	rnode = lambda unknow, node: node.right

class QuadirectionalOrientations(BidirectionalOrientations):
	dnode = lambda unknow, node: node.down
	hnode = lambda unknow, node: node.high

# Functions to advanced in the nodes orientations
class PolydirectionalOrientations(QuadirectionalOrientations):
	ldown = lambda unknow, node: node.lddiag
	rdown = lambda unknow, node: node.rddiag
	lhigh = lambda unknow, node: node.lhdiag
	rhigh = lambda unknow, node: node.rhdiag

# Test
class DominoPiece:
	def __init__(self, *, top, tail):
		self.top = top
		self.tail = tail
		self.nextPiece = None

# QUEUES

# Lines base structure to construct gameboard
class LinkedList:
	def __init__(self):
		self.start = None
		self.last = None
		self._nodeBase = BidirectionalNode
	
	def add(self, data=None):
		newNode = self._nodeBase()
		if self.start == None:
			self.start = newNode
			self.last = newNode
		elif self.start.right == None:
			self.start.right = newNode
			self.last = self.start.right
			self.last.left = self.start
		else:
			self.last.right = newNode
			self.last.right.left = self.last
			self.last = self.last.right

		if data != None:
			newNode.data = data
			
	def show(self):
		pointer = self.start

		while pointer != None:
			print(pointer.value)
			pointer = pointer.right

# Lines Base for construct Board on based in linked lists
class BoardLines(LinkedList):
	def __init__(self):
		super().__init__()
		self._nodeBase = PolydirectionalNode

# Queue type buff structure
class PushedQueue:
	def __init__(self, scalable=False, *, max_size=3):
		self.ini = None
		self.end = None
		self.__size = 0
		self.__max_size = None if scalable else max_size
	
	def push(self, data):
		newNode = SimpleNode(data)
		if self.ini == None:
			self.ini = newNode; self.end = newNode
		else:
			self.end.next = newNode; self.end = newNode
		
		if self.__size == self.__max_size:
			self.ini = self.ini.next
		else:
			self.__size += 1
	
	def erease(self):
		self.ini, self.end = None, None
		self.__size = 0
	
	def __len__(self): return self.__size
			
	def transformToBinCode(self):
		ret = ''
		pointer = self.ini
		while pointer != None:
			ret += f'{1 if pointer.data != None else 0}'
			pointer = pointer.next
		return ret

	def __str__(self):
		ret = ''
		pointer = self.ini
		while pointer != None:
			ret += f'{pointer.data if pointer.data != None else "-"}'
			pointer = pointer.next
		return ret

class PushedNPullsQueue(PushedQueue):
	def pull(self, element):
		pastpointer = None
		pointer = self.ini

		for i in range(element):
			pastpointer = pointer
			pointer = pointer.next

		if element == 0:
			self.ini = pointer.next
		else:
			pastpointer.next = pointer.next

		self._PushedQueue__size -= 1
		return pointer.data

	def pushInterval(self, nodeQueue):
		lastpointer = None
		if self.ini == None:
			self.ini = nodeQueue
			#; self.end = nodeQueue
		else:
			self.end.next = nodeQueue

		pointer = nodeQueue
		while pointer != None:
			self._PushedQueue__size += 1
			lastpointer = pointer
			pointer = pointer.next
		
		self.end = lastpointer

	def pullInterval(self, i, f):
		pastpointer = None
		lastpointer = self.ini
		pointer = self.ini
		newQueue = None

		for z in range(i):
			pastpointer = pointer
			pointer = pointer.next

			self._PushedQueue__size -= 1

		for w in range(f-i):
			pointer = pointer.next
			lastpointer = pointer

			self._PushedQueue__size -= 1

		if not pastpointer:
			newQueue = self.ini
			self.ini = lastpointer.next
		else:
			newQueue = pastpointer.next
			pastpointer.next = lastpointer.next

		lastpointer.next = None
		newQueueForm = PushedNPullsQueue(max_size=f-i+1)
		newQueueForm.pushInterval(newQueue)
		return newQueueForm

	def onFirst(self, data):
		if self.__size == self.__max_size and not self.scalable:
			return
		else:
			self.__size += 1

		newNode = SimpleNode(data)

		if self.ini != None:
			newNode.next = self.ini
			self.ini = newNode
		else:
			self.ini = newNode; self.end = newNode

# Queue of the players
class PlayersQueue(PushedQueue):
	def __init__(self, *, quantity):
		super().__init__(max_size=quantity)

	@property
	def actual(self):
		return self.ini.data

	@property
	def nextplayer(self):
		return self.ini.next.data
		
# GAME BASES

# Gameboard base structure for games
class Board(PolydirectionalOrientations):
	#def __new__(cls, *args, **kwargs):
	#	pass
	def __init__(self, *, width=3, height=3):
		self.width = width; self.height = height
		self.head = None
		self.create(width, height)
		self.__makewhithnodewhencleaning = None

	def create(self, width, height):
		past_line = None
		pastpointer = None; linepointer = None
		
		for i in range(height):
			line = BoardLines()

			for z in range(width):
				line.add()

			if past_line:
				pastpointer = past_line.start
				linepointer = line.start
				
				# Create references
				while linepointer != None:
					pastpointer.down = linepointer
					linepointer.high = pastpointer
					pastpointer.lddiag = linepointer.left
					pastpointer.rddiag = linepointer.right
					linepointer.lhdiag = pastpointer.left
					linepointer.rhdiag = pastpointer.right

					# Update pointers
					pastpointer = pastpointer.right
					linepointer = linepointer.right
			else:
				self.head = line.start
				line.start.link = line.last
				line.last.link = line.start
			# Memorizing current line to iterate with future line
			past_line = line

	def resize(self):
		pass

	def clean(self):
		linepointer = self.head
		while linepointer != None:
			nodepointer = linepointer
			while nodepointer != None:
				nodepointer.data = None
				if self.__makewhithnodewhencleaning != None:
					self.__makewhithnodewhencleaning(nodepointer)
				nodepointer = self.rnode(nodepointer)
			linepointer = self.dnode(linepointer)
			
	def doOnCleanNode(self, action):
		self.__makewhithnodewhencleaning = action

	def __len__(self):
		return self.width * self.height
		