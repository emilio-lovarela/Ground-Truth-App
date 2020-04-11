import glob, os
import pathlib
from PIL import Image, ImageDraw
from io import BytesIO
from zipfile import ZipFile
from shapely.geometry import Polygon
from kivy.config import Config
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
# Config.set('graphics','resizable',False)
# Config.set('graphics', 'fullscreen', True)

from kivy.app import App
from kivy.properties import NumericProperty, ListProperty, \
		BooleanProperty, StringProperty, ObjectProperty
from kivy.uix.stacklayout import StackLayout
from kivy.uix.image import CoreImage
from kivy.graphics import Line, Color
from kivy.core.window import Window # Just in windows?
from MFileChooser import MFileChooser, ChangeClass, Options
from Image_formats import Compress_image, Volume_image
from Color_palette import color_palette

class LinePlay(StackLayout):

	path = ''
	default_path = os.getcwd()
	default_path = default_path.replace("\\", "/", 10) + "\\" "Instrucctions.jpg"

	# General Properties
	obj = MFileChooser()
	path_change = '' # Control changes in path
	options_class = Options()
	change_class = ChangeClass()
	write_mode = BooleanProperty(False)
	load_path = ""
	do_copy = True
	mode = StringProperty("Segmentation")
	id_instance = 1
	
	vol_dimension = BooleanProperty(True)
	max_dime = NumericProperty(1)
	close = BooleanProperty(False)
	disa = BooleanProperty(True)
	points = ListProperty([])
	final_points = ListProperty([])
	final_lpoints = ListProperty([])
	bounding_csv = []
	wait_cont = []
	priority_draw = {} # Control hierarchy features

	# Class variables
	colors_lis = ListProperty([])
	class_name = StringProperty("class1")
	class_color = ListProperty([color_palette[3]/255, color_palette[4]/255, color_palette[5]/255, 1])
	class_number = 1

	# Images list names
	images = glob.glob(path + '*.jpg') + glob.glob(path + '*.png')
	lista_ima = "" # To filter used images
	LImages = len(images) - 1
	filter_boolean = False
	img = StringProperty(images[0])
	file_name = StringProperty(os.path.basename(images[0]))
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

		# Keyboard listen
		self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
		self._keyboard.bind(on_key_down=self._on_keyboard_down)

		# Control window size possibilities
		Window.bind(on_resize=self.window_size_control)
		self.windows_sizes = [Window.size]
		Window.maximize() # Just work in windows?
		self.windows_sizes.append(Window.size)

	# Allow two sizes
	def window_size_control(self, _, t, r):
		if len(self.windows_sizes) == 2:
			if t == self.windows_sizes[1][0] and r == self.windows_sizes[1][1]:
				return
			else:
				Window.size = self.windows_sizes[0]
		else:
			return

	# Function to Popup
	def fire_popup(self, pops, filechooser):
		if filechooser == "filechooser":
			pops.bind(on_dismiss=self.update_path)
		elif filechooser == "chan_class":
			self.change_class.keycode = ""
			self.change_class.filter_view() # Reiniciate view
			pops.bind(on_dismiss=self.update_class)
		elif filechooser == "options":
			pops.bind(on_dismiss=self.update_options)

		pops.open()

	# Function called by clock to update de current path
	def update_path(self, _):
		# If path change, then change images dir
		if self.path_change != self.obj.path:
			# Evaluate the 4 possibilites
			if self.obj.cu_state == "2D": # 2D images in a folder
				new_path = self.obj.path.replace(os.path.sep, '/') + "/"
				self.images = glob.glob(new_path + '*.jpg') + glob.glob(new_path + '*.png') + glob.glob(new_path + '*.BMP') + glob.glob(new_path + '*.tiff') + glob.glob(new_path + '*.tif') + glob.glob(new_path + '*.jfif') + glob.glob(new_path + '*.jpge')
				self.img = self.images[0]

				# Filename and extension
				self.file_name, self.extension = os.path.splitext(os.path.basename(self.img))
				self.image_car.size = Image.open(self.img).size
				self.vol_dimension = True
			elif self.obj.cu_state == "Volume": # .nii or .nii.gz volume
				self.ima_volume = Volume_image(self.obj.path)
				self.vol_dimension = self.ima_volume.dimension
				self.max_dime = self.ima_volume.max_dime
				self.image_car.texture = self.ima_volume.texture
				self.images = [x for x in range(self.ima_volume.lenght)] # Create slice list numeration
				self.image_car.size = self.ima_volume.size

				# Filename and extension
				vol_name, self.extension = os.path.splitext(os.path.basename(self.obj.path))
				self.vol_name, extension = os.path.splitext(vol_name)
				self.extension = extension + self.extension

				# Update filename with correct dimensions code
				if self.vol_dimension == True:
					self.file_name = self.vol_name + "_" + str(0)
				else:
					self.file_name = self.vol_name + "_" + str(0) + "_" + str(0)
			elif self.obj.cu_state == "Compress": # zip 2D files
				self.ima_compress = Compress_image(self.obj.path)
				self.images = self.ima_compress.images_names
				bytes_im = BytesIO(self.ima_compress.z_file.read(self.images[0])) # Convert img into bytes
				
				# Filename and extension
				self.file_name, self.extension = os.path.splitext(os.path.basename(self.images[0]))
				self.zip_name, _ = os.path.splitext(self.images[0])
				self.image_car.texture = CoreImage(bytes_im, ext=self.extension[1:].lower()).texture
				self.image_car.size = Image.open(bytes_im).size
				self.vol_dimension = True

			# Common factors
			self.slider_max.max = len(self.images) - 1
			self.slider_max.value = 0
			self.disa = False
			self.tex_control = ""
			self.switchid.disabled = False

			# Reiniciate factors
			self.x_factor = 0
			self.y_factor = 0
			self.zoom_val = 0
			self.switchid.active = False
			self.filter_boolean = False
			self.path_change = self.obj.path
			self.final_points = []
			self.final_lpoints = []
			self.canvas.remove_group('Lines')
			self.points = []
			self.lpoints = []
			self.colors_lis = []
			self.bounding_csv = []
			self.wait_cont = []
			self.anla_ya.do_layout()
			self.ori_size = self.image_car.size

	# Update class and return keyboard normal control
	def update_class(self, _):

		self.class_name = self.change_class.class_name
		self.class_color = self.change_class.class_color
		self.class_number = self.change_class.classes.get(self.class_name)
		self.write_mode = False
		self.load_path = self.change_class.load_path

	# Update mode of options
	def update_options(self, _):
		self.mode = self.options_class.mode

		# Reiniciate factors
		self.final_points = []
		self.final_lpoints = []
		self.canvas.remove_group('Lines')
		self.points = []
		self.lpoints = []
		self.colors_lis = []
		self.bounding_csv = []
		self.wait_cont = []
		self.tex_control = ""

	def changeimage(self, value, value2):
		self.close = False # Reiniciate close line
		if len(self.images) < 1:
			self.img = self.default_path
			self.file_name = os.path.basename(self.default_path)
			im_size = Image.open(self.default_path)
			self.image_car.size = im_size.size
			self.tex_control = " All Images have masks!"
			self.disa = True
		else:
			# Evaluate the 4 possibilities
			if self.obj.cu_state == "2D":
				self.img = self.images[int(value)]
				self.file_name, self.extension = os.path.splitext(os.path.basename(self.img))
				im_size = Image.open(self.img)
				self.image_car.size = im_size.size
			elif self.obj.cu_state == "Compress":
				bytes_im = BytesIO(self.ima_compress.z_file.read(self.images[int(value)])) # Convert img into bytes
				self.file_name, self.extension = os.path.splitext(os.path.basename(self.images[int(value)]))
				self.zip_name, _ = os.path.splitext(self.images[int(value)])
				self.image_car.texture = CoreImage(bytes_im, ext=self.extension[1:].lower()).texture
				self.image_car.size = Image.open(bytes_im).size
			elif self.obj.cu_state == "Volume":
				self.ima_volume.change_slice(int(value), int(value2)) # change the slice position
				self.image_car.texture = self.ima_volume.texture
				self.image_car.size = self.ima_volume.size

				# Update filename with correct dimensions code
				if self.vol_dimension == True:
					self.file_name = self.vol_name + "_" + str(int(value))
				else:
					self.file_name = self.vol_name + "_" + str(int(value)) + "_" + str(int(value2))
					self.max_dime = self.ima_volume.max_dime

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
		if image.replace(image[image.rfind("."):], "_mask.png")[image.rfind("\\") + 1: ] not in self.lista_ima:
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

		# Handle bounding boxes mode clicks
		if self.mode == "Bounding_boxes" and len(self.points) > 0:
			self.points = []

		# Grab Clicks
		touch.grab(self)
		self.points.append(touch.pos)
		return True

	def on_touch_move(self, touch):
		# Prevent empty list errors
		if not self.points:
			return True

		if self.mode == "Bounding_boxes":
			if touch.grab_current is self:
				if len(self.points) > 3:
					del self.points[-4:]

				# Append new points
				ext_lis = [(touch.pos[0], self.points[0][1]), touch.pos, (self.points[0][0], touch.pos[1]), self.points[0]]
				self.points.extend(ext_lis)
				return True
		else:
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

		# Shortcuts
		if self.write_mode == False:
			move_value = 40

			if keycode[1] == 'up':
				self.zoom_in()
			elif keycode[1] == 'down':
				self.zoom_out()
			elif keycode[1] == 'r' and self.mode != "Bounding_boxes":
				if self.points:
					self.points.pop()
			elif keycode[1] == 'f':
				self.new_line(True)
				self.tog_bu.state = "normal"
			elif keycode[1] == 'spacebar':
				self.write_mode = True
				self.fire_popup(self.change_class, False)
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
		else:
			if keycode[1] == 'right':
				# Change to next image
				if self.slider_max.value < self.slider_max.max:
					if self.filter_boolean == False:
						self.slider_max.value += 1
					else:
						self.slider_max.value -= 1
						self.slider_max.value += 1
			elif keycode[1] == 'left':
				# Change to before image
				if self.slider_max.value > self.slider_max.min:
					self.slider_max.value -= 1
			else:
				self.change_class.keyboard_grab(keycode[1])

	# Zoom in and out functions
	def zoom_in(self):

		# Update list points zoom in
		self.points = [(x[0] - (self.image_car.center_x - x[0]) + self.x_factor, x[1] - (self.image_car.center_y - x[1]) + self.y_factor) for x in self.points]
		
		# Update final point lists
		self.final_points = [[(x[0] - (self.image_car.center_x - x[0]) + self.x_factor, x[1] - (self.image_car.center_y - x[1]) + self.y_factor) for x in y] for y in self.final_points]
		
		# Removing painted lines
		self.canvas.remove_group('Lines')

		# Adding new Lines
		for i, color in zip(self.final_points, self.colors_lis):
			with self.canvas:
				Color(color_palette[color * 3]/255, color_palette[(color * 3) + 1]/255, color_palette[(color * 3) + 2]/255, 1)
				Line(points=i, group='Lines')

		# Update image size and pos (Handling updated error)
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
		for i, color in zip(self.final_points, self.colors_lis):
			with self.canvas:
				Color(color_palette[color * 3]/255, color_palette[(color * 3) + 1]/255, color_palette[(color * 3) + 2]/255, 1)
				Line(points=i, group='Lines')

		# Update image and pos size (Because updated error)
		self.image_car.size[0] = self.image_car.size[0] / 2
		self.image_car.size[1] = self.image_car.size[1] / 2
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
		for i, color in zip(self.final_points, self.colors_lis):
			with self.canvas:
				Color(color_palette[color * 3]/255, color_palette[(color * 3) + 1]/255, color_palette[(color * 3) + 2]/255, 1)
				Line(points=i, group='Lines')

	# Remove instance or contour added
	def undo_instance(self):

		# Search element position
		try:
			index = self.colors_lis.index(self.class_number)
		except:
			return

		# Handle instance mode del instance contours
		if self.mode == "Instance" or self.mode == "Bounding_boxes":
			indices = [index]
			compro = self.bounding_csv[index]
			if isinstance(compro[-1], str) == True: # Check id

				index2 = 0
				for item in self.bounding_csv:
					if item[-1] == compro[-1] and index2 != index:
						indices.append(index2)
					index2 += 1

			for ind in sorted(indices, reverse=True):
				# Remove element from list and update canvas
				del self.final_points[ind]
				del self.colors_lis[ind]
				del self.bounding_csv[ind]
		else:
			# Remove element from list
			del self.final_points[index]
			del self.colors_lis[index]

		# Removing painted lines
		self.canvas.remove_group('Lines')

		# Adding new Lines
		for i, color in zip(self.final_points, self.colors_lis):
			with self.canvas:
				Color(color_palette[color * 3]/255, color_palette[(color * 3) + 1]/255, color_palette[(color * 3) + 2]/255, 1)
				Line(points=i, group='Lines')

	def new_line(self, bounding):
		# Handling empty list error
		if not self.points or len(self.points) == 1:
			self.close = False # Reiniciate close line
			return

		# Final point list
		self.points.append(self.points[0])

		# If mode is instance calculate bounding boxes and append to list.
		if bounding == True and (self.mode == "Instance" or self.mode == "Bounding_boxes"):
			points = self.points
			points = self.prepare_box(points)
			self.wait_cont.extend(points)

			# Calculate x y w h
			x, y = self.wait_cont[0]
			w, h = self.wait_cont[0]
			for poi in self.wait_cont:
				new_x, new_y = poi

				# Update values
				if new_x > w:
					w = new_x
				if new_x < x:
					x = new_x
				if new_y > h:
					h = new_y
				if new_y < y:
					y = new_y

			# CSV list
			if self.tex_control == "Contour mode":
				list_csv = [self.class_name, x, y, w, h, str(self.id_instance)]
				self.id_instance += 1
				self.tex_control = ""
			else:
				list_csv = [self.class_name, x, y, w, h]

			# Reiniciate wait list
			self.wait_cont = []
		elif self.mode == "Instance":
			list_csv = [str(self.id_instance)]

		# Create points polygon
		new_polygon = Polygon(self.points)
		self.close = False # Reiniciate close line

		# Removing painted lines
		self.canvas.remove_group('Lines')

		# Draw new lines and insert in position
		compro_hiera = True
		insert_position = -1
		for points, color, position in zip(self.final_points, self.colors_lis, range(len(self.colors_lis))):

			# Insert if contour inside it
			polyb = Polygon(points)
			if compro_hiera == True:
				if new_polygon.contains(polyb):
					compro_hiera = False
					insert_position = position

			with self.canvas:
				Color(color_palette[color * 3]/255, color_palette[(color * 3) + 1]/255, color_palette[(color * 3) + 2]/255, 1)
				Line(points=points, group='Lines')

		# Insert point in final_points list
		if compro_hiera == False:
			self.final_points[insert_position:insert_position] = [self.points]
			self.colors_lis[insert_position:insert_position] = [self.class_number]

			if self.mode == "Instance" or self.mode == "Bounding_boxes":
				self.bounding_csv[insert_position:insert_position] = [list_csv]
		else:
			self.final_points.append(self.points)
			self.colors_lis.append(self.class_number)

			if self.mode == "Instance" or self.mode == "Bounding_boxes":
				self.bounding_csv.append(list_csv)

		with self.canvas:
			Color(color_palette[self.class_number* 3]/255, color_palette[(self.class_number* 3) + 1]/255, color_palette[(self.class_number* 3) + 2]/255, 1)
			Line(points=self.points, group='Lines')

		# Reiniciate points		
		self.points = []

	# Put a mark to save bounding boxes
	def new_contour(self):
		# Handling empty list error
		if not self.points or len(self.points) == 1:
			self.close = False # Reiniciate close line
			return

		# Save Bounding boxes original position
		points = self.points
		points.append(points[0])
		points = self.prepare_box(points)

		self.wait_cont.extend(points)
		self.tex_control = "Contour mode"
		self.new_line(False)

	# Prepare bounding_boxes
	def prepare_box(self, points):
		copy = self.zoom_val
		points = [(x[0] + self.x_factor, x[1] + self.y_factor) for x in points]
		if copy > 0:
			for val in range(0, copy):
				points = [(((self.image_car.center_x + self.x_factor + x[0])/2), ((self.image_car.center_y + self.y_factor + x[1])/2)) for x in points]
		elif copy < 0:
			for val in range(0, abs(copy)):
				points = [(x[0] - (self.image_car.center_x + self.x_factor - x[0]), x[1] - (self.image_car.center_y + self.y_factor - x[1])) for x in points]

		return points

	def save_image(self):

		# Change points to final_points list
		self.new_line(True)

		# Updating image to default position
		copy = self.zoom_val
		if copy > 0:
			for val in range(0, copy):
				self.zoom_out()
		elif copy < 0:
			for val in range(0, abs(copy)):
				self.zoom_in()

		if self.mode == "Instance" or self.mode == "Segmentation":
			# Generated mask
			final_image = Image.new("P", [int(round(self.ori_size[0])),int(round(self.ori_size[1]))])
			
			# Activate color_palette
			final_image.putpalette(color_palette)
			draw = ImageDraw.Draw(final_image)

			# Updating last points in list
			self.final_lpoints = [[(x[0] - self.image_car.pos[0], self.image_car.size[1] - (x[1] - self.image_car.pos[1])) for x in y] for y in self.final_points]

			# Drawing lines
			for i in range(len(self.final_lpoints)):
				draw.polygon(self.final_lpoints[i], fill=self.colors_lis[i], outline=self.colors_lis[i])

		# Saved final image in mask folder
		if self.obj.cu_state == "2D":
			folder_path = self.obj.path + "_masks"
			csv_path = self.obj.path + "_csv_tag_color.txt"
			csv_folder = self.obj.path + "_csv"
			final_path = folder_path + "/" + self.file_name + "_mask.png"
			csv_final_path = csv_folder + "/" + self.file_name + "_csv.txt"
		else:
			folder_path = os.path.dirname(self.obj.path) + "_masks"
			csv_folder = os.path.dirname(self.obj.path) + "_csv"

			if self.obj.cu_state == "Volume": # Save in new volume folder
				csv_path = folder_path.replace("_masks", "_csv_tag_color.txt")
				folder_path = folder_path + "/" + os.path.basename(self.obj.path.replace(self.extension, ""))
				csv_folder = csv_folder + "/" + os.path.basename(self.obj.path.replace(self.extension, ""))
				final_path = folder_path + "/" + self.file_name + "_mask.png"
				csv_final_path = csv_folder + "/" + self.file_name + "_csv.txt"
			else:
				csv_path = folder_path.replace("_masks", "/") + os.path.basename(self.obj.path.replace(".zip", "_csv_tag_color.txt"))
				final_path = folder_path + "/" + os.path.basename(self.obj.path.replace(".zip", "")) + "/" + self.zip_name + "_mask.png"
				csv_final_path = csv_folder + "/" + os.path.basename(self.obj.path.replace(".zip", "")) + "/" + self.zip_name + "_csv.txt"
				folder_path = os.path.dirname(final_path)
				csv_folder = os.path.dirname(csv_final_path)

		# Save mask in folder. Create folder if doenst exists
		if self.mode == "Instance" or self.mode == "Segmentation":
			pathlib.Path(folder_path).mkdir(parents=True, exist_ok=True)
			final_image.save(final_path)

			# Check if load_path is active
			if self.load_path != "":
				csv_path = self.load_path
			else:
				# Copy for prevent user save error
				if os.path.exists(csv_path) and self.do_copy == True:
					csv_path = csv_path.replace(".txt", "_copy.txt")

			# Write csv files
			if len(self.change_class.classes) > 1:
				with open(csv_path, mode='w') as file:
					file.write("background\t0")
					for item in self.change_class.classes:
						file.write("\n" + item + "\t" + str(self.change_class.classes.get(item)))

		# Save bounding boxes in instance mode
		if self.mode == "Instance" or self.mode == "Bounding_boxes":

			# Create csv image
			pathlib.Path(csv_folder).mkdir(parents=True, exist_ok=True)
			with open(csv_final_path, mode='w') as file:

				# Updating bounding_csv
				for items in self.bounding_csv:
					if len(items) == 5:
						clas, x, y, w, h = items
					elif len(items) == 6:
						clas, x, y, w, h, _ = items
					else:
						continue

					# Calculate points reference and save
					x = x - self.image_car.pos[0] - self.x_factor if x - self.image_car.pos[0] - self.x_factor > 0 else 0
					w = w - self.image_car.pos[0] - self.x_factor if w - self.image_car.pos[0] - self.x_factor < self.image_car.size[0] else self.image_car.size[0]
					y = y - self.image_car.pos[1] - self.y_factor if y - self.image_car.pos[1] - self.y_factor > 0 else 0
					h = h - self.image_car.pos[1] - self.y_factor if h - self.image_car.pos[1] - self.y_factor < self.image_car.size[1] else self.image_car.size[1]
					w = w - x
					h = h - y

					# If caption active add caption popup
					write_line = clas + "\t" + str(round(x)) + "\t" + str(round(y)) + "\t" + str(round(w)) + "\t" + str(round(h)) + "\n"
					file.write(write_line)

		# Reiniciate zoom_val and seeds
		self.zoom_val = 0

		# Check if filter is actived
		if self.switchid.active == True:
			self.filter_boolean = True
		self.do_copy = False

class GroundTruthBuilder(App):
	def build(self):
		return LinePlay()


if __name__ == '__main__':
	GroundTruthBuilder().run()