from structureBase import Board, PushedQueue, PlayersQueue
from random import choice


# FUNCTIONS AND FEATURES

class LoadGame:
	islocalplayer = lambda instance, player: isinstance(player, LocalPlayer)
	isnonlocalplayer = lambda instance, player: isinstance(player, NonLocalPlayer)
	isunrealplayer = lambda instance, player: isinstance(player, UnrealPlayer)
	
	def __init__(self, nplayers, boardsize, iaplayer=True):
		self.gameisload = self.__start(nplayers, boardsize, iaplayer)
		self.game_state_tags = 'null', 'incourse', 'closed'
		
	def __start(self, nplayers, boardsize, iaplayer):
		if (1 < nplayers < 4) and TicTacToe._isvalidsize(boardsize):
			self.game = TicTacToe(nplayers=nplayers, width=boardsize[0], height=boardsize[1])
			self.judge = GameSupervisor(self.game)
	
			for i in range(nplayers - (1 if iaplayer else 0)):
				self.judge.addPlayer(LocalPlayer())
				#self.judge.addPlayer(UnrealPlayer())
	
			if iaplayer:
				self.judge.addPlayer(UnrealPlayer())
			
			self.judge.distributePieces()

			return True
		return False

	def getPlayer(self):
		return self.judge.currentPlayer
	
	# RASCUNHOS	E	IDEIAS
	def change_variables(self, nplayers, boardsize, iaplayer):
		if (1 < nplayers < 4) and TicTacToe._isvalidsize(boardsize):
			self.gameisload = True
			
			#self.game.resize(size=boardsize)
			
	def moveProccess(self):
		pass
			
# GAME

class TicTacToe(Board):
	def __init__(self, *, nplayers, width=3, height=3):
		Board.__init__(self, width=width, height=height)

		condiction = 2 < self.width < 5 or 2 < self.height < 5

		self.nplayers = nplayers
		self.min_align = 3 if condiction or nplayers == 3 else 4
		self.patternSPEC = [2**self.min_align - 1]
		self.free = width*height
		self.anyWon = False
		self.__makewithdata = None
		self.__status = 0
		self.dependency_to_start = False
		self.game_state_tags = {0:'null', 1:'incourse', 2:'closed'}
		
	def doOnSetData(self, action):
		self.__makewithdata = action
		
	def doOnCleanNode(self, action):
		super().doOnCleanNode(action)
		
	def setDataByIndex(self, *, index, data):
		pointer = self.head
		for i in range(index // self.width):
			pointer = pointer.down
		for i in range(index % self.width):
			pointer = pointer.right
		if pointer.data == None:
			pointer.data = data
			self.free -= 1

			if self.__makewithdata != None:
				self.__makewithdata(node=pointer, data=data)
			
			return True
		return False
	
	def setDataByNode(self, *, node, data):
		if node.data == None:
			node.data = data
			self.free -= 1

			self.__makewithdata(node=node, data=data)
			
			return True
		return False

	def resize(self, size):
		pass
		
	def clean(self):
		super().clean()
		self.__status = 0
		self.free = self.width*self.height
		self.anyWon = False
	
	def open(self):
		self.dependency_to_start = True
	
	# Update state of the game and return state when function is called 
	def updateGameEnv(self):
		ret = self.__status
		
		if (self.free == 0 or self.anyWon) and self.__status == 1:
			ret = self.__status = 2
		elif self.dependency_to_start == True and self.__status == 0:
			self.dependency_to_start = False
			ret = self.__status = 1
			
		return ret
	
	# Return a correspondent tag of the state
	@property
	def status(self):
		return self.game_state_tags[self.updateGameEnv()]
		
	@classmethod
	def _isvalidsize(cls, size):
		w, h = size
		min, max = 2, 7

		t = isinstance(size, tuple)
		l = len(size) == 2
		i = min <= w <= max and min <= h <= max

		return all((t, l, i))
		
		
# PLAYERS

class LocalPlayer:
	def __init__(self):
		self.id = None # for online matches, future implementation
		self.name = None
		self.piece = None
		self.gameBoard = None
		self.playerChoice = None
	
	def makeAPlay(self):
		set = self.gameBoard.setDataByIndex
		move = set(index=self.playerChoice, data=self.piece)
		return move
		
class UnlocalPlayer:
	def __init__(self):
		self.id = None # for online matches, future implementation
		self.name = None
		self.piece = None
		self.gameBoard = None
		self.playerChoice = None
		
	def makeAPlay(self):
		pass

class UnrealPlayer:
	def __init__(self):
		self.id = 0 # for online matches, future implementation
		self.name = None
		self.piece = None
		self.gameBoard = None
		self.options = None
		self.opponentBlock = None
		self.strategicMove = None
		
	def checkSelfPossibilityToWin(self):
		board = self.gameBoard
		piece = self.piece
		gets = self.getDatas

		SPEC = [3, 5, 6] if board.min_align == 3 else [7, 11, 13, 14]

		scans = (gets.scanLines, gets.scanColls, gets.scanLDiags, gets.scanRDiags)

		for scan in scans:
			scanOutput = scan(board, char=piece, externalSPEC=SPEC)
			if scanOutput:
				return scanOutput
		return None

	def checkRivalPossibilityToWin(self):
		board = self.gameBoard
		piece = self.nextPlayerPiece
		gets = self.getDatas

		SPEC = [3, 5, 6] + [7, 10, 11, 12, 13, 14]*(board.min_align == 4)

		scans = (gets.scanLines, gets.scanColls, gets.scanLDiags, gets.scanRDiags)
		
		for scan in scans:
			scanOutput = scan(board, char=piece, externalSPEC=SPEC)
			if scanOutput:
				return scanOutput
		return None

	def checkStrategyPossibility(self):
		board = self.gameBoard
		piece = self.piece
		gets = self.getDatas

		SPEC = [1, 2, 4] + [8, 10, 12]*(board.min_align == 4)

		scans = (gets.scanLines, gets.scanColls, gets.scanLDiags, gets.scanRDiags)

		for scan in scans:
			scanOutput = scan(board, char=piece, externalSPEC=SPEC)
			if scanOutput:
				return scanOutput
		return None

	def makeAChoice(self):
		# First play
		if self.gameBoard.free == len(self.gameBoard):
			return

		avaliable = self.checkSelfPossibilityToWin()
		if avaliable:
			self.strategicMove = avaliable.emptyNode
			return

		avaliable = self.checkRivalPossibilityToWin()
		if avaliable:
			self.opponentBlock = avaliable.emptyNode
			return

		avaliable = self.checkStrategyPossibility()
		if avaliable:
			self.strategicMove = avaliable.emptyNode
			return
	
	def makeAPlay(self):
		self.makeAChoice()
		setindex = self.gameBoard.setDataByIndex
		setnode = self.gameBoard.setDataByNode

		if self.opponentBlock:
			move = setnode(node=self.opponentBlock, data=self.piece)
			self.opponentBlock = None

		elif self.strategicMove:
			move = setnode(node=self.strategicMove, data=self.piece)
			self.strategicMove = None

		else:
			move = False
			while not move:
				sortedChoice = choice(self.options)
				move = setindex(index=sortedChoice, data=self.piece)
				self.options.remove(sortedChoice)

		return move


# JUDGE

class GameSupervisor:
	def __init__(self, gameBoard):
		self.gameBoard = gameBoard
		self.playersRow = PlayersQueue(quantity=gameBoard.nplayers)
		self.currentPlayer = None

	def addPlayer(self, player):
		self.playersRow.push(player)

	def __scanBase(self, board, char, pointer, node_move, externalSPEC):
		SPEC = externalSPEC if externalSPEC else board.patternSPEC
		lockcheck = 0
		toeval = PushedQueue(max_size=board.min_align)
		node = pointer
		while node != None:
			value = node.data
			if value == None:
				toeval.emptyNode = node
				toeval.push(None)
			elif value == char:
				toeval.push(char)
			else:
				toeval.push(None)
				lockcheck = 1
			if lockcheck:
				lockcheck = (lockcheck + 1) % (board.min_align + 1)
			elif len(toeval) == board.min_align:
				bin_to_dec = int(toeval.transformToBinCode(), 2)
				if bin_to_dec in SPEC:
					return toeval
			try:
				node = node_move(node)
			except:
				node = None
		return None

	def scanLines(self, board, *, char, externalPointer=None, externalSPEC=None):
		pointer = board.head if not externalPointer else externalPointer
		while pointer != None:
			node = self.__scanBase(board, char, pointer, board.rnode, externalSPEC)
			if node:
				return node
			pointer = board.dnode(pointer) if not externalPointer else None
		return None
	
	def scanColls(self, board, *, char, externalPointer=None, externalSPEC=None):
		pointer = board.head if not externalPointer else externalPointer
		while pointer != None:
			node = self.__scanBase(board, char, pointer, board.dnode, externalSPEC)
			if node:
				return node
			pointer = board.rnode(pointer) if not externalPointer else None
		return None
	
	def setIniDiagsPointer(self, board, right_diags=False):
		pointer = board.head.link if right_diags else board.head
		for i in range(board.width-board.min_align):
			if right_diags: pointer = board.lnode(pointer)
			else: pointer = board.rnode(pointer)
		return pointer

	def diagsPointerMotion(self, board, *, right_diags=False):
		initial_moves = board.rnode if right_diags else board.lnode
		move = lambda pointer: initial_moves(pointer) or board.dnode(pointer)
		return move

	def scanLDiags(self, board, *, char, externalPointer=None, externalSPEC=None):
		pointer = self.setIniDiagsPointer(board, right_diags=False)
		pointer_move = self.diagsPointerMotion(board, right_diags=False)
		n_ldiags = (board.width+board.height-(2*board.min_align)+1)
		
		count = 0
		while pointer != None:
			count = (count + 1) % n_ldiags
			node = self.__scanBase(board, char, pointer, board.rdown, externalSPEC)
			pointer = None if (not count or externalPointer) else pointer_move(pointer)
			if node:
				return node
		return None
		
	def scanRDiags(self, board, *, char, externalPointer=None, externalSPEC=None):
		pointer = self.setIniDiagsPointer(board, right_diags=True)
		pointer_move = self.diagsPointerMotion(board, right_diags=True)
		n_rdiags = (board.width+board.height-(2*board.min_align)+1)
		
		count = 0
		while pointer != None:
			count = (count + 1) % n_rdiags
			node = self.__scanBase(board, char, pointer, board.ldown, externalSPEC)
			pointer = None if (not count or externalPointer) else pointer_move(pointer)
			if node:
				return node
		return None

	def checkWon(self):
		board = self.gameBoard
		player = self.currentPlayer

		scans = (self.scanLines, self.scanColls, self.scanLDiags, self.scanRDiags)
		
		for scan in scans:
			scanOutput = scan(board, char=player.piece)
			if scanOutput != None:
				return True
		return False

	def callNextPlayer(self):
		self.playersRow.push(self.currentPlayer)
		player = self.currentPlayer = self.playersRow.actual

#		if isinstance(player, UnrealPlayer):
#			player.makeAChoice()
#			player.makeAPlay()
#			
#			if self.checkWon():
#				self.gameBoard.anyWon = True
#			else:
#				self.callNextPlayer()
			

	def distributePieces(self):
		quantity = len(self.playersRow)
		player_pointer = self.playersRow.ini
		self.currentPlayer = self.playersRow.actual

		for piece in range(quantity):
			playerDatas = player_pointer.data
			playerDatas.gameBoard = self.gameBoard
			playerDatas.piece = piece
			# Logic for unreal player
			if playerDatas.id == 0: # id equals zero if player isn't a real player
				playerDatas.nextPlayerPiece = (piece + 1) % quantity
				playerDatas.getDatas = self
				playerDatas.options = [i for i in range(len(self.gameBoard))]

			player_pointer = player_pointer.next
			
	def resetGame(self):
		board = self.gameBoard
		player_pointer = self.playersRow.ini
		
		board.clean()
		
		while player_pointer != None:
			if isinstance(player_pointer.data, UnrealPlayer):
				player_pointer.data.options = [i for i in range(len(self.gameBoard))]
			player_pointer = player_pointer.next
			