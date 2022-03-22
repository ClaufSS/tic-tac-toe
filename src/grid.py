from kivy.graphics.stencil_instructions import StencilPush, StencilUse, StencilUnUse, StencilPop
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import Screen
from kivy.graphics import Color, Line, Rectangle
from kivy.properties import StringProperty
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.clock import Clock
from game import LoadGame
from tm import TC

timers = TC()
ld = LoadGame(nplayers=2, boardsize=(5,5))

# Create screen to the game
class GameScreen(Screen):
	def on_pre_enter(self, *args):
		self.ids.lay.start()
		
	def on_pre_leave(self, *args):
		self.ids.lay.stop()

# Create a time counter base
class Counter(Label):
	markerTarget = StringProperty()
	
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.t = None
		self.time_status = 'null'
		self.halign = 'center'
		self.font_name = 'playmegames'
		
	def start(self, offset=0):
		timers.set_timeMarker(marker=self.markerTarget, persistent=True, offset=offset)
		self.time_status = 'running'
		self.update()
		
	def stop(self):
		self.time_status = 'stoped'
		
	def clean(self):
		if self.time_status == 'null':
			return
			
		timers.destroy(marker=self.markerTarget)
		self.time_status = 'null'
		self.text = ''
		
	def update(self):
		self.t = timers.get_timeMarker(marker=self.markerTarget)
		self.text = timers.time_transform(self.t)
		

class Cell(Image):
	def __init__(self, i, j, **kwargs):
		super().__init__(**kwargs)
		self.i, self.j = i, j
		self.source = ''
		
	def on_size(self, *args):
		lay = self.parent.ids.lay
		thicknessPercentX = lay.thickness/self.parent.width
		thicknessPercentY = lay.thickness/self.parent.height
		hintX = self.i*(lay.size_hint_x/lay.grid_w) + lay.pos_hint.get('x') + thicknessPercentX/2
		hintY = self.j*(lay.size_hint_y/lay.grid_h) + lay.pos_hint.get('y') + thicknessPercentY/2
		hintW = lay.size_hint_x/lay.grid_w - thicknessPercentX
		hintH = lay.size_hint_y/lay.grid_h - thicknessPercentY
		
		self.size_hint = hintW, hintH
		self.pos_hint = {'x': hintX, 'y': hintY}
		
	def on_source(self, *args):
		if self.source == '':
			self.color = (0,0,0,0)
		else:
			self.color = (0,0,0,.2)
		
# Creating the grid plan
class BoardLay(Widget):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.grid_w, self.grid_h = ld.game.width, ld.game.height
		self.linewidth = 2
		self.selectedCell = None
		self.celulesState = False
		self.event = None

	def on_touch_down(self, touch):
		if self.collide_point(touch.x, touch.y):
			halfthickness = self.thickness/2
			
			min_x, min_y = (halfthickness/self.x_interval), (halfthickness/self.y_interval)	
			max_x, max_y = 1 - min_x, 1 - min_y
			
			tracking_x = (touch.x - self.x)/self.x_interval
			tracking_y = (touch.y - self.y)/self.y_interval
			
			if (min_x < tracking_x - tracking_x//1 < max_x) and (min_y < tracking_y - tracking_y//1 < max_y):
				i = tracking_x//1
				j = tracking_y//1

				q = (j-self.grid_h+1)*-1
				index = int(i + q*self.grid_w)

				if self.selectedCell == None:
					self.selectedCell = index
				return True
		return super().on_touch_down(touch)

	def update(self, *args):
		halfthickness = self.thickness/2
		
		self.canvas.before.clear()
		with self.canvas.before:
			#Color(rgba=(1,1,1,1))
			Color(rgba=(0,0,0,1))
			
			StencilPush()

			Rectangle(
				size=(self.width - 2*self.thickness, self.height - 2*self.thickness),
				pos=(self.x + self.thickness, self.y + self.thickness)
				)
			
			StencilUse()
			# Draw rounded rectangles in background
			w, h = self.x_interval - self.thickness, self.y_interval - self.thickness
			for i in range(self.grid_h):
				y_s = self.y_interval*(i) + self.y + halfthickness
				for j in range(self.grid_w):
					x_s = self.x_interval*(j) + self.x + halfthickness
			
					Line(width=self.linewidth, rounded_rectangle=((x_s, y_s) + (w, h) + (halfthickness,)*4))
				
			StencilUnUse()

			Rectangle(
				size=(self.width - 2*self.thickness, self.height - 2*self.thickness),
				pos=(self.x + self.thickness, self.y + self.thickness)
				)

			StencilPop()
			
			for i in range(1, self.grid_w):
				x_s = self.x + self.x_interval*i - halfthickness
				y_s = self.y + self.thickness
				
				Line(width=self.linewidth, points=(x_s, y_s, x_s + self.thickness, y_s))

				y_s += self.height - self.thickness*2
				
				Line(width=self.linewidth, points=(x_s, y_s, x_s + self.thickness, y_s))
			
			for i in range(1, self.grid_h):
				x_s = self.x + self.thickness
				y_s = self.y + self.y_interval*i - halfthickness
				
				Line(width=self.linewidth, points=(x_s, y_s, x_s, y_s + self.thickness))

				x_s += self.width - self.thickness*2
				
				Line(width=self.linewidth, points=(x_s, y_s, x_s, y_s + self.thickness))

	def loadCells(self, *args):
		pieceStyle = 'shapes'
		imagePath = 'images/'
		
		source = lambda data, imagePath=imagePath, pieceStyle=pieceStyle: imagePath + pieceStyle + '-' + str(data) + '.png'
		
		def  actionset(node, data):
			node.referencetolay.source = source(data)

		def actionclean(node):
			node.referencetolay.source = ''
			
		board = ld.game
		board.doOnSetData(actionset)
		board.doOnCleanNode(actionclean)
		
		i = 0
		primary_pointer = board.head
		while primary_pointer != None:
			j = 0
			secondary_pointer = primary_pointer
			while secondary_pointer != None:
				q = (i-board.height+1)*-1
				
				pieceReference = Cell(j, q)
				
				secondary_pointer.referencetolay = pieceReference
				self.parent.add_widget(pieceReference)
				secondary_pointer = board.rnode(secondary_pointer)
				j += 1
			primary_pointer = board.dnode(primary_pointer)
			i += 1
			
		self.celulesState = True
			
	
	def gameInteractive(self, *args):
		# GameTime Piece
		tmgpiece = self.parent.ids.tmg
		# PlayerTime Piece
		tmppiece = self.parent.ids.tmp
		
		if ld.game.status == 'incourse':
			player = ld.getPlayer()
			played = False
			if ld.islocalplayer(player):
				if self.selectedCell != None:
					player.playerChoice = self.selectedCell
					self.selectedCell = None
					
					if player.makeAPlay():
						tmppiece.stop()
						played = True
							
			elif ld.isunrealplayer(player):
				if player.makeAPlay():
					played = True
					
			elif ld.isnonlocalplayer(player):
				pass
				
			if played:
				if ld.judge.checkWon():
					ld.game.anyWon = True
				elif ld.game.free != 0:
					ld.judge.callNextPlayer()
					
		else:
			if ld.game.anyWon:
				self.parent.ids.posi.text = str(type(ld.judge.currentPlayer)) + ' ganhou!'
			elif ld.game.free == 0:
				self.parent.ids.posi.text = 'Empate!'
		
		# GameTime actions depending on the states of the game
		if tmgpiece.time_status == 'running' and ld.game.status == 'closed':
			tmgpiece.stop()
			
		if tmgpiece.time_status == 'stoped' and ld.game.status == 'closed' and self.selectedCell != None:
			tmgpiece.clean()
			ld.judge.resetGame()
			self.selectedCell = None
			self.parent.ids.posi.text = ''
				
		if tmgpiece.time_status == 'null' and ld.game.status == 'null':
			tmgpiece.start()
			ld.game.open()
		
		# Update counters time
		if tmgpiece.time_status == 'running':
			tmgpiece.update()
		if tmppiece.time_status == 'running':
			tmppiece.update()
		
		# PlayerTime actions 
		if ld.islocalplayer(ld.getPlayer()):
			if tmppiece.time_status == 'stoped' and ld.game.status == 'incourse':
				tmppiece.clean()
			if tmppiece.time_status == 'null' and ld.game.status == 'incourse':
				tmppiece.start(offset=0)
				
	def start(self, *args):
		if not self.celulesState:
			self.loadCells()
		self.event = Clock.schedule_interval(self.gameInteractive, 1/30)
		
	def stop(self, *args):
		#Clock.unschedule_interval(self.event)
		pass	