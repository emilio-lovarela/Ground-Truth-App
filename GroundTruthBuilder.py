import glob, os
from PIL import Image, ImageDraw
from kivy.app import App
from kivy.properties import NumericProperty, ListProperty, \
		BooleanProperty, StringProperty, ObjectProperty
from kivy.uix.stacklayout import StackLayout
from kivy.lang import Builder
from kivy.graphics import Line
from kivy.config import Config
from kivy.core.window import Window # Just in windows?
from MFileChooser import MFileChooser, PopupButton

from kivy.event import EventDispatcher
from kivy.clock import Clock

Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
# Config.set('graphics', 'fullscreen', True)

class LinePlay(StackLayout):

	path = ''
	default_path = os.getcwd()
	default_path = default_path.replace("\\", "/", 10) + "\\" "Instrucctions.jpg"

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
	lista_ima = "" # To filter used images
	LImages = len(images) - 1
	filter_boolean = False
	img = StringProperty(images[0])
	image_car = ObjectProperty() # Extract relative positions

	# Text vanish
	tex_control = StringProperty("")

	# Move corretion factor
	x_factor = 0
	y_factor = 0

	# Variables to save
	ori_size = ListProperty([])
	zoom_val = 0
	
	# Functions
	def __init__(self, **kwargs):
		super(LinePlay, self).__init__(**kwargs)

		# Keyboard isten
		self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
		self._keyboard.bind(on_key_down=self._on_keyboard_down)

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
				im_size = Image.open(self.img)
				self.image_car.size = im_size.size
				self.disa = False
				self.tex_control = ""
				self.switchid.disabled = False

				# Reiniciate factors
				self.x_factor = 0
				self.y_factor = 0
				self.ori_size = self.image_car.size
				self.zoom_val = 0
				self.switchid.active = False
				self.filter_boolean = False

			self.lis.pop(0)

	def changeimage(self, value):
		self.close = False # Reiniciate close line
		if len(self.images) < 1:
			self.img = self.default_path
			im_size = Image.open(self.default_path)
			self.image_car.size = im_size.size
			self.tex_control = " All Images have masks!"
			self.disa = True
		else:
			self.img = self.images[int(value)]
			im_size = Image.open(self.img)
			self.image_car.size = im_size.size

		# Reiniciate factors
		self.x_factor = 0
		self.y_factor = 0
		self.zoom_val = 0

		# Check if filter is actived
		if self.filter_boolean == True:
			self.filter_boolean = False # Reiniciate default state
			valu = self.slider_max.value
			self.filter_images(True)
			self.slider_max.value = valu

	# Functions to filter used images in dir
	def filter_type(self, image):
		if image.replace(image[image.rfind("."):], "_mask" + image[image.rfind("."):])[image.rfind("\\") + 1: ] not in self.lista_ima:
			return True

	def filter_images(self, state):
		if os.path.exists(self.obj.path + "_masks"):
			if state == True:
				self.lista_ima = os.listdir(self.obj.path + "_masks")
				self.images = list(filter(self.filter_type, self.images))
			else:
				new_path = self.obj.path.replace(os.path.sep, '/') + "/"
				self.images = glob.glob(new_path + '*.jpg') + glob.glob(new_path + '*.png') + glob.glob(new_path + '*.BMP') + glob.glob(new_path + '*.tiff')
				self.filter_boolean = False # Reiniciate default state
				self.disa = False
		else:
			self.tex_control = " No masks!"
			self.switchid.active = False
			return

		# Reiniciate slider values
		self.slider_max.max = len(self.images) - 1
		self.slider_max.value = 0

	# Handle touchs
	def on_touch_down(self, touch):
		if super(LinePlay, self).on_touch_down(touch):
			return True

		# Scrolling detection for zoom in and zoom out	
		if touch.is_mouse_scrolling:
			if touch.button == 'scrolldown':
				self.zoom_in()
				return True

			elif touch.button == 'scrollup':
				self.zoom_out()
				return True

		# Grab Clicks
		self.tex_control = ""
		touch.grab(self)
		self.points.append(touch.pos)
		return True

	def on_touch_move(self, touch):
		if touch.grab_current is self:
			self.points[-1] = touch.pos
			return True
		return super(LinePlay, self).on_touch_move(touch)

	def on_touch_up(self, touch):
		if touch.grab_current is self:
			touch.ungrab(self)
			return True
		return super(LinePlay, self).on_touch_up(touch)

	# keyboard controler
	def _keyboard_closed(self):
		self._keyboard.unbind(on_key_down=self._on_keyboard_down)
		self._keyboard = None

	def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
		move_value = 40

		if keycode[1] == 'up':
			self.zoom_in()
		elif keycode[1] == 'down':
			self.zoom_out()
		elif keycode[1] == 'right' or keycode[1] == "e":
			# Change to next image
			if self.slider_max.value < self.slider_max.max:
				if self.filter_boolean == False:
					self.slider_max.value += 1
				else:
					self.slider_max.value -= 1
					self.slider_max.value += 1
		elif keycode[1] == 'left' or keycode[1] == "q":
			# Change to before image
			if self.slider_max.value > self.slider_max.min:
				self.slider_max.value -= 1
		elif keycode[1] == 'w' or 's' or 'a' or 'd':
			self.move_in(keycode[1])

	# Zoom in and out functions
	def zoom_in(self):

		# Update list points zoom in
		self.points = [(x[0] - (self.image_car.center_x - x[0]) + self.x_factor, x[1] - (self.image_car.center_y - x[1]) + self.y_factor) for x in self.points]
		
		# Update final point lists
		self.final_points = [[(x[0] - (self.image_car.center_x - x[0]) + self.x_factor, x[1] - (self.image_car.center_y - x[1]) + self.y_factor) for x in y] for y in self.final_points]
		
		# Removing painted lines
		self.canvas.remove_group('Lines')

		# Adding new Lines
		for i in range(0,len(self.final_points)):
			with self.canvas:
				Line(points=self.final_points[i], group='Lines')

		# Update image size and pos (Handling updated error)
		self.image_car.pos[0] = self.image_car.pos[0] - self.image_car.size[0] / 2
		self.image_car.pos[1] = self.image_car.pos[1] - self.image_car.size[1] / 2

		self.image_car.size[0] = self.image_car.size[0] * 2
		self.image_car.size[1] = self.image_car.size[1] * 2

		self.anla_ya.do_layout()

		# Reiniciate factors
		self.x_factor = 0
		self.y_factor = 0
		self.zoom_val += 1

	def zoom_out(self):

		# Update list points zoom out
		self.points = [(((self.image_car.center_x + x[0])/2) + self.x_factor, ((self.image_car.center_y + x[1])/2) + self.y_factor) for x in self.points]
		
		# Update final point lists
		self.final_points = [[(((self.image_car.center_x + x[0])/2) + self.x_factor, ((self.image_car.center_y + x[1])/2) + self.y_factor) for x in y] for y in self.final_points]
		
		# Removing painted lines
		self.canvas.remove_group('Lines')

		# Adding new Lines
		for i in range(0,len(self.final_points)):
			with self.canvas:
				Line(points=self.final_points[i], group='Lines')

		# Update image and pos size (Because updated error)
		self.image_car.size[0] = self.image_car.size[0] / 2
		self.image_car.size[1] = self.image_car.size[1] / 2

		self.image_car.pos[0] = self.image_car.size[0] / 2 + self.image_car.pos[0]
		self.image_car.pos[1] = self.image_car.size[1] / 2 + self.image_car.pos[1]

		self.anla_ya.do_layout()
		
		# Reiniciate factors
		self.x_factor = 0
		self.y_factor = 0
		self.zoom_val -= 1

	# Move image to x positions updating the list points
	def move_in(self, param):
		if param == 'w':
			self.image_car.pos[1] = self.image_car.pos[1] + 40

			# Update list points move
			self.points = [(x[0], x[1] + 40) for x in self.points]
			# Update final list points
			self.final_points = [[(x[0], x[1] + 40) for x in y] for y in self.final_points]
			# Update y factor
			self.y_factor -= 40

		elif param == 's':
			self.image_car.pos[1] = self.image_car.pos[1] - 40

			# Update list points move
			self.points = [(x[0], x[1] - 40) for x in self.points]
			# Update final list points
			self.final_points = [[(x[0], x[1] - 40) for x in y] for y in self.final_points]
			# Update y factor
			self.y_factor += 40

		elif param == 'd':
			self.image_car.pos[0] = self.image_car.pos[0] + 40

			# Update list points move
			self.points = [(x[0] + 40, x[1]) for x in self.points]
			# Update final list points
			self.final_points = [[(x[0] + 40, x[1]) for x in y] for y in self.final_points]
			# Update x factor
			self.x_factor -= 40

		elif param == 'a':
			self.image_car.pos[0] = self.image_car.pos[0] - 40

			# Update list points move
			self.points = [(x[0] - 40, x[1]) for x in self.points]
			# Update final list points
			self.final_points = [[(x[0] - 40, x[1]) for x in y] for y in self.final_points]
			# Update x factor
			self.x_factor += 40

		# Removing painted lines
		self.canvas.remove_group('Lines')

		# Adding new Lines
		for i in range(0,len(self.final_points)):
			with self.canvas:
				Line(points=self.final_points[i], group='Lines')

	def new_line(self):
		# Handling empty list error
		if not self.points:
			self.close = False # Reiniciate close line
			return

		# Final point list
		self.points.append(self.points[0])
		
		self.final_points.append(self.points)
		self.points = []
		self.close = False # Reiniciate close line

		for i in range(0,len(self.final_points)):
			with self.canvas:
				Line(points=self.final_points[i], group='Lines')

	def save_image(self):

		# Generated mask
		final_image = Image.new("RGB", [int(round(self.ori_size[0])),int(round(self.ori_size[1]))])
		draw = ImageDraw.Draw(final_image)

		# Updating image to default position
		copy = self.zoom_val
		if copy > 0:
			for val in range(0, copy):
				self.zoom_out()
		elif copy < 0:
			for val in range(0, abs(copy)):
				self.zoom_in()

		# Updating last points in list
		self.lpoints = [(x[0] - self.image_car.pos[0], self.image_car.size[1] - (x[1] - self.image_car.pos[1])) for x in self.points]
		self.final_lpoints = [[(x[0] - self.image_car.pos[0], self.image_car.size[1] - (x[1] - self.image_car.pos[1])) for x in y] for y in self.final_points]

		# Drawing lines
		if not self.lpoints or len(self.lpoints) == 1:
			for i in self.final_lpoints:
				draw.polygon(i, fill="White", outline='white')
		else:
			for i in self.final_lpoints:
				draw.polygon(i, fill="White", outline='white')

			# Close line
			self.lpoints = self.lpoints + [self.lpoints[0]]
			draw.polygon(self.lpoints, fill="White", outline='white')

		# Saved final image in mask folder
		filename = self.img.replace(self.img[self.img.rfind("\\"): ], "_masks")
		
		# Create folder to save masks if doesnt exist
		if not os.path.exists(filename):
			os.makedirs(filename)

		filename = filename + self.img[self.img.find("\\"): ]
		filename = filename.replace(".jpg", "_mask.jpg").replace(".BMP", "_mask.BMP").replace(".png", "_mask.png").replace(".tiff", "_mask.tiff")
		final_image.save(filename)

		# Reiniciate zoom_val and seeds
		self.zoom_val = 0
		self.close = True
		self.tog_bu.state = "down"

		# Check if filter is actived
		if self.switchid.active == True:
			self.filter_boolean = True

class GroundTruthBuilder(App):
	def build(self):
		return LinePlay()


if __name__ == '__main__':
	Window.maximize() # Just work in windows?
	GroundTruthBuilder().run()