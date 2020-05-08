from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.storage.jsonstore import JsonStore
from kivy.properties import StringProperty, ObjectProperty, DictProperty, ListProperty, BooleanProperty

from os.path import isdir, exists, isfile
from zipfile import ZipFile
from threading import Thread
from Color_palette import text_render_size, color_palette, text_labels
from Dropbox_link import LoadCsvDopbox

Builder.load_file("MFileChooser.kv")

# FIleChooser class
class MFileChooser(Popup):

	path = StringProperty('')
	RootPath = StringProperty('/')
	Invalid_Path = StringProperty('')
	store = JsonStore('RootPath.json')
	cu_state = "2D" # Possibilities 2D, Volume, Video, Compress

	def __init__(self):
		super(MFileChooser, self).__init__()
		# Load Rootpath if exists
		if self.store.exists('RootPath'):
			if exists(self.store.get('RootPath')['Path']) == True:
				self.RootPath = self.store.get('RootPath')['Path']

	def is_not_dir(self, files):
		# Method for filter files/folders
		for i in files:
			if isfile(i):
				return True
		return False

	def path_exist(self, file_path):
		if not exists(file_path):
			self.Invalid_Path = "Invalid Path!"

		else:
			# Store the value of RootPath
			self.store.put('RootPath', Path=file_path)

			# Update RootPath
			self.RootPath = file_path
			self.Invalid_Path = "Root Changed!"

	# Return path with 2d images format
	def dismiss_popup_images(self):
		self.path = self.filecho.path
		self.Invalid_Path = ''
		self.cu_state = "2D"
		self.dismiss()

	# Return volume or compress file
	def dismiss_popup_volume(self):
		# Handle empty list error
		if self.filecho.selection:
			if self.filecho.selection[0].lower().endswith(('.nii', '.nii.gz')) == True:
				self.path = self.filecho.selection[0]
				self.Invalid_Path = ''
				self.cu_state = "Volume"
				self.dismiss()
			elif self.filecho.selection[0].lower().endswith(('.zip')) == True:

				# Check if images in file
				z_file = ZipFile(self.filecho.selection[0], mode="r")
				name_li = ZipFile.namelist(z_file)
				images_names = [i for i in name_li if i.lower().endswith(('.png', '.jpg', '.jpeg', '*.jfif', ".tiff", ".tif", ".bmp"))] # Filter list of images
				z_file.close()

				if images_names: # Update information
					self.path = self.filecho.selection[0]
					self.Invalid_Path = ''
					self.cu_state = "Compress"
					self.dismiss()
				else:
					self.Invalid_Path = 'No images in Zip!'

# FIleChooser load/save csv
class Loadcsv(Popup):
	load_path = ""
	dic_classes = {}
	RootPath = StringProperty('/')
	store = JsonStore('RootPath.json')

	def __init__(self):
		super(Loadcsv, self).__init__()
		# Load Rootpath if exists
		if self.store.exists('RootPath'):
			if exists(self.store.get('RootPath')['Path']) == True:
				self.RootPath = self.store.get('RootPath')['Path']

	def dismiss_file(self, file_path):
			# Read CSV and update dictionary
			self.dic_classes = {}
			with open(file_path, mode='r') as file:
				first = file.readline()
				for line in file:
					try:
						key, value = line.split("\t")
						value = int(value)
					except:
						continue

					# Check if value its a int number
					if value > 1:
						if key != "background" and key != "borders":
							self.dic_classes[key] = value

			# Check fails
			if len(self.dic_classes) == 0:
				self.dismiss()
				return

			self.load_path = file_path
			self.dismiss()

# Classes, categories (dog, cat, human...) Popup
class ChangeClass(Popup):

	# Variables and kivy properties
	load_class = Loadcsv()
	load_class_dropbox = LoadCsvDopbox()
	load_path = ""
	keycode = StringProperty("class1")
	classes = DictProperty()
	current_class = ObjectProperty()
	class_name = StringProperty("class1")
	class_color = ListProperty([color_palette[6]/255, color_palette[7]/255, color_palette[8]/255, 1])
	
	advice = StringProperty("")
	block = False
	shift = False
	max_num = 3
	not_used_num = []
	mode = StringProperty("normal") # normal, edit, remove
	save_clasi = False
	clasifi = False
	running_thread = False
	using_dropbox = BooleanProperty(False)

	# Charge default values
	def __init__(self):
		super(ChangeClass, self).__init__()

		width = self.calculate_render_len()
		button = Button(text=self.class_name, size_hint=(None, None), size=(width, 30), font_size=20, valign="middle")
		
		# Bind function to the button
		button.bind(on_press=self.button_calback)

		# Format the button
		button.color = [0,0,0,1]
		color_num = 2
		button.background_normal = ""
		button.background_color = self.class_color
		self.ids.grid.add_widget(button)

		# Classes dictionary and current class
		self.classes[self.class_name] = 2
		self.current_class = button
		self.keycode = ""


	# Add current class if not exist
	def new_class(self, lock_file):

		if self.mode == "edit":
			if self.block == True:
				# If class text is empty, or used return advice
				if self.current_class.text == "" or self.current_class.text == "background" or self.current_class.text == "borders":
					self.advice = "Invalid name!"
				elif self.classes.get(self.current_class.text) != None and self.current_class.text != self.class_name:
					self.advice = "Class name already exists!"
				else:
					# Update dictionary with new key old value
					self.classes[self.current_class.text] = self.classes.pop(self.class_name)
					self.class_name = self.current_class.text

					# Activate all buttons again
					self.normaler.disabled = False
					self.remover.disabled = False
					for button in self.ids.grid.children.copy():
						button.disabled = False
					
					self.block = False
					self.advice = "" # Delete advice text

				# Reiniciate filter
				self.keycode = ""
				return
			else:
				# Return advice
				self.advice = "No class selected!"
				return
		elif self.mode == "remove":
			# Eliminate class if exists
			if self.current_class == "":
				return
			elif len(self.classes) == 1:
				self.advice = "A class is necessary!"
				return
			elif self.classes.get(self.current_class.text) != None:
				self.not_used_num.append(self.classes.pop(self.class_name))
				self.ids.grid.remove_widget(self.current_class)
				self.class_name = ""
				return


		# Normal mode options
		# Handle empty classes
		if len(self.keycode) == 0 or self.keycode == "background" or self.keycode == "borders":
			self.advice = "Invalid name!"
			return

		# Check if using dropbox and if must lock dropbox file
		if self.using_dropbox == True and lock_file == True:
			self.advice = "No in dropbox mode!"
		else:
			self.create_class()

	# Auxiliar function for new class
	def create_class(self):
		# Fill dic with new value
		if self.classes.get(self.keycode) == None:
			if self.not_used_num:
				self.classes[self.keycode] = self.not_used_num.pop()
			else:
				self.classes[self.keycode] = self.max_num
				self.max_num += 1
		else:
			self.auto_dismiss = True
			self.advice_label.color = (1,0,0,1)
			self.advice = "Class already exists!"
			self.running_thread = False
			return

		width = self.calculate_render_len()
		button = Button(text=self.keycode, size_hint=(None, None), size=(width, 30), font_size=20, valign="middle")
		
		# Bind function to the button
		button.bind(on_press=self.button_calback)

		# Format the button
		button.color = [0,0,0,1]
		color_num = self.classes[self.keycode]
		button.background_normal = ""
		button.background_color = [color_palette[color_num * 3]/255, color_palette[(color_num * 3) + 1]/255, color_palette[(color_num * 3) + 2]/255, 1]
		self.ids.grid.add_widget(button)

		# Reiniciate keycode
		self.keycode = ""
		if self.running_thread == True:
			self.auto_dismiss = True
			self.advice_label.color = (1,0,0,1)
			self.running_thread = False

	# Edit class names
	def change_class(self):

		# Modify class widget
		width = self.calculate_render_len()
		self.current_class.text = self.keycode
		self.current_class.size = (width, 30)
		self.current_class.valign = "middle"

	# Calculate the button width to fit the text
	def calculate_render_len(self):
		width = 0
		for symbol in self.keycode:
			value = text_render_size.get(symbol)
			if value == None:
				value = 9
			width += value

		# Minime size of button
		if width < 5:
			width = 5

		return width + 8
	
	# Filter classes view with keycode
	def filter_view(self):
		for button in self.ids.grid.children.copy():
			if button.text.startswith(self.keycode):
				button.color = (0,0,0,1)
				button.background_color[-1] = 1
				button.disabled = False
			else:
				self.ids.grid.remove_widget(button)
				self.ids.grid.add_widget(button)
				button.disabled = True
				button.color = (0,0,0,0)
				button.background_color[-1] = 0

	# Button callback function
	def button_calback(self, instance):

		self.advice = ""
		self.current_class = instance
		self.class_name = instance.text
		self.class_color = instance.background_color
		if self.mode == "normal":
			self.save_clasi = True
			self.dismiss()
		elif self.mode == "edit":
			self.block = True
			self.keycode = instance.text

			# Disabled all buttons except selected
			self.normaler.disabled = True
			self.remover.disabled = True
			for button in self.ids.grid.children.copy():
				if button != instance:
					button.disabled = True

	# Fire different popup using dropbox
	def fire_popup(self):
		if self.using_dropbox == False:
			self.load_class.bind(on_dismiss=self.update_classes)
			self.load_class.open()
		else:
			self.load_class_dropbox.bind(on_dismiss=self.update_classes_dropbox)
			self.load_class_dropbox.background_load() # Create the representation
			self.load_class_dropbox.open()

	# Update classes from csv callback
	def update_classes(self, _):
		# Handle auto dismiss error
		if self.load_path == self.load_class.load_path:
			return

		self.load_path = self.load_class.load_path
		self.not_used_num = list(self.load_class.dic_classes.values())
		self.not_used_num.reverse()
		self.max_num = max(self.not_used_num) + 1
		not_used_num = [x for x in range(self.max_num - 1) if x not in self.not_used_num and x not in [0,1]]

		# Update widgets and dictionary
		classes = self.load_class.dic_classes
		self.classes = {}
		self.ids.grid.clear_widgets()
		for item in classes:
			self.keycode = item
			self.new_class(False)

		# Update text and current class
		if self.clasifi == False:
			self.button_calback(self.ids.grid.children[-1])

		self.not_used_num = not_used_num # Update not_used_num

	# Update classes from csv in dropbox callback
	def update_classes_dropbox(self, drop_compro):

		# If classes is empty dont update
		if not self.load_class_dropbox.dic_classes:
			self.advice = "No classes in csv!"
			return

		# Update control variables
		self.load_path = self.load_class_dropbox.load_path
		self.not_used_num = list(self.load_class_dropbox.dic_classes.values())
		self.not_used_num.reverse()
		self.max_num = max(self.not_used_num) + 1
		not_used_num = [x for x in range(self.max_num - 1) if x not in self.not_used_num and x not in [0,1]]

		# Update widgets and dictionary
		classes = self.load_class_dropbox.dic_classes
		self.classes = {}
		self.ids.grid.clear_widgets()
		for item in classes:
			self.keycode = item
			self.new_class(False)

		# Update text and current class
		if drop_compro != True:
			self.button_calback(self.ids.grid.children[-1])
			self.advice = ""

		self.not_used_num = not_used_num # Update not_used_num

	# Keyboard write grab
	def keyboard_grab(self, keycode):
		# Reiniciate advise
		self.advice = ""

		if keycode == "backspace":
			self.keycode = self.keycode[:-1]
		elif keycode == "spacebar":
			self.keycode = self.keycode + " "
		elif keycode == "enter":
			self.new_class(True)
		elif keycode == "capslock" or keycode == "shift" or keycode == "tab" or keycode == "lctrl" or keycode == "rctrl":
			pass
		elif keycode == "up" or keycode == "down" or keycode == "left" or keycode == "right":
			pass
		elif keycode == "rshift": # Allow use _
			self.shift = True
		elif keycode == "-":
			if self.shift == True:
				self.keycode = self.keycode + "_"
			else:
				self.keycode = self.keycode + keycode
		else:
			self.shift = False
			self.keycode = self.keycode + keycode

		# Limit the text size
		if len(self.keycode) > 32:
			self.keycode = self.keycode[:-1]

		# Filter view
		if self.block == False:
			self.filter_view()
		else:
			self.change_class()

# Options class
class Options(Popup):
	mode = StringProperty("Segmentation") # Clasification, Bounding_boxes, Segmentation, Instance
	description = StringProperty(text_labels.get("Segmentation"))
	borders = BooleanProperty(False)
	dropbox = BooleanProperty(False)

	# Update description
	def change_description(self, key):
		self.mode = key
		self.description = text_labels.get(key)