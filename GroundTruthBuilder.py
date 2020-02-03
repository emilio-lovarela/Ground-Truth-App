import glob, os
from functools import partial
from PIL import Image, ImageDraw
from kivy.app import App
from kivy.properties import NumericProperty, ListProperty, \
        BooleanProperty, StringProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.graphics import Line
from kivy.config import Config
from MFileChooser import MFileChooser, PopupButton

from kivy.event import EventDispatcher
from kivy.clock import Clock

Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

class LinePlay(BoxLayout):

	path = ''
	# General Properties
	obj = MFileChooser()
	lis = [] # Control changes in path
	
	alpha_controlline = NumericProperty(1.0)
	close = BooleanProperty(False)
	disa = BooleanProperty(True)
	points = ListProperty([])
	lpoints = ListProperty([])
	final_points = ListProperty([])
	final_lpoints = ListProperty([])

	# Images list names
	images = glob.glob(path + '*.jpg') + glob.glob(path + '*.png')
	LImages = len(images) - 1
	img = StringProperty(images[0])
	image_car = ObjectProperty() # Extract relative positions
	
	# Text vanish
	tex_control = StringProperty("")
	
	# Functions
	def __init__(self):
		super(LinePlay, self).__init__()

		# Iniciate Clock function
		Clock.schedule_interval(self.update_path,.1)

	# Function called by clock to update de current path
	def update_path(self, dt):
		self.lis.append(self.obj.path)
		if len(self.lis) == 2:
			if self.lis[0] != self.lis[1]:
				# If path change, then change images dir.
				new_path = self.obj.path.replace(os.path.sep, '/') + "/"
				self.images = glob.glob(new_path + '*.jpg') + glob.glob(new_path + '*.png') + glob.glob(new_path + '*.BMP') + glob.glob(new_path + '*.tiff')
				self.slider_max.max = len(self.images) - 1
				self.slider_max.value = 0
				self.img = self.images[0]
				self.disa = False

			self.lis.pop(0)

	def changeimage(self, value):
		self.close = False # Reiniciate close line
		self.img = self.images[int(value)]

	def on_touch_down(self, touch):
		if super(LinePlay, self).on_touch_down(touch):
			return True
		touch.grab(self)
		self.points.append(touch.pos)
		self.lpoints.append((touch.x - self.image_car.pos[0], self.image_car.size[1] - (touch.y - self.image_car.pos[1])))
		return True

	def on_touch_move(self, touch):
		if touch.grab_current is self:
			self.points[-1] = touch.pos
			self.lpoints[-1] = (touch.x - self.image_car.pos[0], self.image_car.size[1] - (touch.y - self.image_car.pos[1]))
			return True
		return super(LinePlay, self).on_touch_move(touch)

	def on_touch_up(self, touch):
		if touch.grab_current is self:
			touch.ungrab(self)
			return True
		return super(LinePlay, self).on_touch_up(touch)   

	def save_image(self, size, pos):
		# Generated mask
		final_image = Image.new("RGB", [int(round(size[0])),int(round(size[1]))])
		draw = ImageDraw.Draw(final_image)

		# Drawing lines
		if not self.lpoints or len(self.lpoints) == 1:
			for i in self.final_lpoints:
				draw.line(i, fill="White", width=1)
		else:
			for i in self.final_lpoints:
				draw.line(i, fill="White", width=1)

			# Close line
			if self.close == True:
				draw.line(self.lpoints + [self.lpoints[0]], fill="White", width=1)
			else:
				draw.line(self.lpoints, fill="White", width=1)

		# Saved final image in mask folder
		filename = self.img.replace(self.img[self.img.rfind("/"): ], "/masks")
		
		# Create folder to save masks if doesnt exist
		if not os.path.exists(filename):
			os.makedirs(filename)

		filename = filename + self.img[self.img.find("\\"): ]
		filename = filename.replace(".jpg", "_mask.jpg").replace(".BMP", "_mask.BMP").replace(".png", "_mask.png").replace(".tiff", "_mask.tiff")
		final_image.save(filename)
		# print("size: ", size, " pos: ", pos, self.points, self.lpoints)

	def new_line(self):
		# Handling empty list error
		if not self.points:
			self.close = False # Reiniciate close line
			return

		# Final point list
		if self.close == True:
			self.points.append(self.points[0])
			self.lpoints.append(self.lpoints[0])
		
		self.final_points.append(self.points)
		self.final_lpoints.append(self.lpoints)
		self.points = []
		self.lpoints = []
		self.close = False # Reiniciate close line

		for i in range(0,len(self.final_points)):
			with self.canvas:
				Line(points=self.final_points[i], group='Lines')


class GroundTruthBuilder(App):
	def build(self):
		return LinePlay()


if __name__ == '__main__':
    GroundTruthBuilder().run()