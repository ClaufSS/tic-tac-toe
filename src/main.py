import json
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.core.text import Label as CoreLabel
from kivy.properties import ListProperty, NumericProperty, ObjectProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from colour import hex2rgb
from grid import *


CoreLabel.register('playmegames', 'fontes/PlaymegamesReguler-2OOee.ttf')
Builder.load_file('grid.kv')


def processColors(add_to):
	colors_collections = json.load()

	colors = colors_collections['light_mode']

	add_to.__dict__.update(colors)


class MenuLayout(BoxLayout):
	def add_widget(self, widget, index=0, canvas=None):
		super().add_widget(widget, index, canvas)
		widget.bind(size=(lambda *args: self.redraw()))
		
	def redraw(self):
		recuo = 100
		
		spacement = self.height / self.chils
		self.canvas.before.clear()
		with self.canvas.before:
			Color(rgba=(.8, .8, .8, 1))
			for child in self.children[1:]:

				chil_x, *k = child.texture_size
				x_i = self.x + (self.width - chil_x)/2 - recuo
				x_f = x_i + chil_x + 2*recuo
				y_i = y_f = child.y

				if x_f - x_i > self.width:
					x_i = self.x
					x_f = x_i + self.width

				Line(width=2, points=(x_i, y_i, x_f, y_f))
				
				
class RoundedBox(FloatLayout):
	reference = ObjectProperty(None)
	radius = ObjectProperty(5)
	segments = NumericProperty(20)
	line_width = NumericProperty(1)
	color = ListProperty((0, 0, 0, 1))
	leakage = NumericProperty(0)

	_colorpattern = (0, 0, 0, 1)
	_radiuspattern = (10, 10, 10, 10)

	def formatColor(self, color, *args):
		color, n = tuple(color), len(color)
		return (color + (() if n == 4 else (1,))) if n in (3, 4) else self._colorpattern

	def getRadiusRules(self, radiusbase, *args):
		if isinstance(radiusbase, int):
			radiusbase = (radiusbase,)

		radiusbase = tuple(radiusbase); n = len(radiusbase)
		return (radiusbase*int(4/n)) if n in (1, 2, 4) else self._radiuspattern

	def chng_size(self, obj, newsize):
		self.size = newsize

	def chng_pos(self, obj, newpos):
		self.pos = newpos

	def on_reference(self, *args):
		#if not self.oldreference == None:
			#self.oldreference.unbind(size)
			#self.oldreference.unbind(pos)

		self.size_hint = None, None
		self.oldreference = self.reference
		self.reference.bind(size=self.chng_size)
		self.reference.bind(pos=self.chng_pos)

class RoundedFillBox(RoundedBox):
	pass

class HomeMenu(Screen):
    pass

class GridSizeMenu(Screen):
    pass
    
class SettingsMenu(Screen):
	pass

class RankingScreen(Screen):
	pass
		
class App(App):
	def build(self):
		sm = ScreenManager(transition=NoTransition())
		sm.add_widget(HomeMenu(name='homemenu'))
		sm.add_widget(GridSizeMenu(name='sizemenu'))
		sm.add_widget(SettingsMenu(name='settingmenu'))
		sm.add_widget(GameScreen(name='gamescreen'))
		sm.add_widget(RankingScreen(name='ranking'))
		Window.clearcolor = hex2rgb("#35322E") + (1,)
		
		return sm

	#def on_start(self, *args):
		#ProcessColors(add_to=self)

App().run()
