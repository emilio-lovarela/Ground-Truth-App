from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.storage.jsonstore import JsonStore
from kivy.properties import StringProperty, ObjectProperty, DictProperty, ListProperty

from os.path import isdir, exists, isfile
from zipfile import ZipFile
from Color_palette import text_render_size, color_palette

Builder.load_file("MFileChooser.kv")

# FIleChooser class
class MFileChooser(Popup):

	path = StringProperty('')
	RootPath = StringProperty('')
	Invalid_Path = StringProperty('')
	store = JsonStore('RootPath.json')
	cu_state = "" # Possibilities 2D, Volume, Video, Compress

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


# Classes, categories (dog, cat, human...) Popup
class ChangeClass(Popup):

	# Variables and kivy properties
	keycode = StringProperty("class1")
	classes = DictProperty()
	current_class = ObjectProperty()
	class_name = StringProperty("class1")
	class_color = ListProperty([color_palette[3]/255, color_palette[4]/255, color_palette[5]/255, 1])
	
	advice = StringProperty("")
	block = False
	shift = False
	max_num = 2
	not_used_num = []
	mode = StringProperty("normal") # normal, edit, remove

	# Charge default values
	def __init__(self):
		super(ChangeClass, self).__init__()

		width = self.calculate_render_len()
		button = Button(text=self.class_name, size_hint=(None, None), size=(width, 30), font_size=20, valign="middle")
		
		# Bind function to the button
		button.bind(on_press=self.button_calback)

		# Format the button
		button.color = [0,0,0,1]
		color_num = 1
		button.background_normal = ""
		button.background_color = self.class_color
		self.ids.grid.add_widget(button)

		# Classes dictionary and current class
		self.classes[self.class_name] = 1
		self.current_class = button
		self.keycode = ""

	# Add current class if not exist
	def new_class(self):

		if self.mode == "edit":
			if self.block == True:
				# If class text is empty, or used return advice
				if self.current_class.text == "":
					self.advice = "Empty name is invalid!"
				elif self.classes.get(self.current_class.text) != None and self.current_class.text != self.class_name:
					self.advice = "Class name already exists!"
				else:
					# Update dictionary with new key old value
					self.classes[self.current_class.text] = self.classes.pop(self.class_name)
					self.class_name = self.current_class.text

					# Activate all buttons again
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
			elif self.classes.get(self.current_class.text) != None:
				self.not_used_num.append(self.classes.pop(self.class_name))
				self.ids.grid.remove_widget(self.current_class)
				self.class_name = ""
				return


		# Normal mode options
		# Handle empty classes
		if len(self.keycode) == 0:
			self.advice = "Empty names not allowed!"
			return

		# Fill dic with new value
		if self.classes.get(self.keycode) == None:
			if self.not_used_num:
				self.classes[self.keycode] = self.not_used_num.pop()
			else:
				self.classes[self.keycode] = self.max_num
				self.max_num += 1
		else:
			self.advice = "Class already exists!"
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
			self.dismiss()
		elif self.mode == "edit":
			self.block = True
			self.keycode = instance.text

			# Disabled all buttons except selected
			for button in self.ids.grid.children.copy():
				if button != instance:
					button.disabled = True

	# Keyboard write grab
	def keyboard_grab(self, keycode):
		# Reiniciate advise
		self.advice = ""

		if keycode == "backspace":
			self.keycode = self.keycode[:-1]
		elif keycode == "spacebar":
			self.keycode = self.keycode + " "
		elif keycode == "enter":
			self.new_class()
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