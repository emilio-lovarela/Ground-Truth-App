#!/usr/bin/env python3

from glob import glob 
from os import getcwd, walk, listdir
from os import remove as remove_f
from os import name as name_system
from os.path import basename, sep, splitext, dirname, relpath, join, exists
from time import sleep
from shutil import rmtree
from pathlib import Path as Pathli
from urllib.request import urlopen
from PIL import Image, ImageDraw
from io import BytesIO
from zipfile import ZipFile
from shapely.geometry import Polygon
from dropbox.files import WriteMode
from threading import Thread
from socket import socket, gethostbyname, gethostname
from datetime import datetime
from pytz import timezone
from kivy.config import Config
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
Config.set('kivy', 'exit_on_escape', '0')
Config.set('kivy','window_icon','icons/icon.png')

from kivy.app import App
from kivy.properties import NumericProperty, ListProperty, \
		BooleanProperty, StringProperty, ObjectProperty
from kivy.uix.stacklayout import StackLayout
from kivy.uix.image import CoreImage
from kivy.graphics import Line, Color
from kivy.storage.jsonstore import JsonStore
from kivy.lang import Builder
from kivy.core.window import Window
from MFileChooser import MFileChooser, ChangeClass, Options
from Image_formats import Compress_image, Volume_image
from Color_palette import color_palette
from Dropbox_link import Dropbox_images
from Client import Chat_multiple, Server_loading
from Server import Server

Builder.load_file("GroundTruthMain.kv")

class LinePlay(StackLayout):

	path = 'instrucctions/'
	default_path = getcwd()
	default_path = default_path.replace("\\", "/", 40) + "\\" "Instrucctions.jpg"

	# General Properties
	obj = MFileChooser()
	path_change = '' # Control changes in path
	options_class = Options()
	change_class = ChangeClass()
	chat_class = Chat_multiple()
	dropbox_class = Dropbox_images()
	server_class = Server()
	server_loading_class = Server_loading()
	write_mode = BooleanProperty(False)
	load_path = ""
	mode = StringProperty("Segmentation")
	id_instance = 1
	borders = False
	dropbox = False
	using_dropbox = False
	
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
	class_color = ListProperty([color_palette[6]/255, color_palette[7]/255, color_palette[8]/255, 1])
	class_number = 2

	# Images list names
	images = glob(path + '*.jpg')
	lista_ima = "" # To filter used images
	LImages = len(images) - 1
	filter_boolean = False
	img = StringProperty(images[0])
	file_name = StringProperty(basename(images[0]))
	image_car = ObjectProperty() # Extract relative positions

	# Text vanish
	tex_control = StringProperty("")

	# Move corretion factor
	x_factor = 0
	y_factor = 0

	# Variables to save
	ori_size = ListProperty([])
	zoom_val = 0

	# Connection variable
	HOST = 'localhost'
	PORT = 33000
	BUFSIZ = 1024
	change_restric = False
	server_instance = False
	drop_filt = False
	ima_used_by_users = {} # Current images in use by some user
	client_socket = -1
	blocking_check_server = False
	
	# Functions
	def __init__(self, **kwargs):
		super(LinePlay, self).__init__(**kwargs)

		# Keyboard listen
		self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
		self._keyboard.bind(on_key_down=self._on_keyboard_down)

		# Control window size possibilities and close
		Window.bind(on_resize=self.window_size_control)
		Window.bind(on_request_close=self.on_request_close)
		self.windows_sizes = [Window.size]
		Window.maximize()
		self.windows_sizes.append(Window.size)

	# Allow two sizes
	def window_size_control(self, _, t, r):
		
		# Check if system is windows
		if name_system != "nt":
			return

		if len(self.windows_sizes) == 2:
			if t == self.windows_sizes[1][0] and r == self.windows_sizes[1][1]:
				return
			else:
				Window.size = self.windows_sizes[0]
		else:
			return

	# Ejecute on close app if using dropbox
	def on_request_close(self, _):
		if self.using_dropbox == True:
			try:
				if self.server_instance == True:
					self.dropbox_class.dbx.files_delete("/Config_Folder/lock_file.txt")
			except:
				pass

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
		elif filechooser == "chat":
			self._keyboard_closed() # Close keyboard to use textinput
			self.chat_class.text_cu_in.multiline = False
			pops.bind(on_dismiss=self.rebind_keyboard)
		elif filechooser == "dropbox":
			pops.bind(on_dismiss=self.update_dropbox)

			# If token selected then update tree structure
			self.tex_control = ""
			pops.background_load()
		pops.open()

	# Reiniciate all values
	def reiniciate_all(self):
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

	# Function called by clock to update de current path
	def update_path(self, _):
		# If path change, then change images dir
		if self.path_change != self.obj.path:
			self.using_dropbox = False
			self.change_class.using_dropbox = False
			self.change_class.load_path = ""
			# Evaluate the 3 possibilites
			if self.obj.cu_state == "2D": # 2D images in a folder
				new_path = self.obj.path.replace(sep, '/') + "/"
				self.images = glob(new_path + '*.jpg') + glob(new_path + '*.png') + glob(new_path + '*.BMP') + glob(new_path + '*.tiff') + glob(new_path + '*.tif') + glob(new_path + '*.jfif') + glob(new_path + '*.jpeg')
				self.img = self.images[0]

				# Filename and extension
				self.file_name, self.extension = splitext(basename(self.img))
				self.image_car.size = Image.open(self.img).size
				self.vol_dimension = True
			elif self.obj.cu_state == "Volume": # .nii or .nii.gz volume
				self.img = "" # Use texture
				self.ima_volume = Volume_image(self.obj.path)
				self.vol_dimension = self.ima_volume.dimension
				self.max_dime = self.ima_volume.max_dime
				self.image_car.texture = self.ima_volume.texture
				self.images = [x for x in range(self.ima_volume.lenght)] # Create slice list numeration
				self.image_car.size = self.ima_volume.size

				# Filename and extension
				vol_name, self.extension = splitext(basename(self.obj.path))
				self.vol_name, extension = splitext(vol_name)
				self.extension = extension + self.extension

				# Update filename with correct dimensions code
				if self.vol_dimension == True:
					self.file_name = self.vol_name + "_" + str(0)
				else:
					self.file_name = self.vol_name + "_" + str(0) + "_" + str(0)
			elif self.obj.cu_state == "Compress": # zip 2D files
				self.img = "" # Use texture
				self.ima_compress = Compress_image(self.obj.path)
				self.images = self.ima_compress.images_names
				bytes_im = BytesIO(self.ima_compress.z_file.read(self.images[0])) # Convert img into bytes
				
				# Filename and extension
				self.file_name, self.extension = splitext(basename(self.images[0]))
				self.zip_name, _ = splitext(self.images[0])
				self.image_car.texture = CoreImage(bytes_im, ext=self.extension[1:].lower()).texture
				self.image_car.size = Image.open(bytes_im).size
				self.vol_dimension = True

			self.reiniciate_all()

	# Class update dropbox images async
	def update_dropbox(self, _):
		if self.dropbox_class.change == False:
			return
		else:
			# Kill is active kill server and update
			if self.dropbox_class.token_class.kill == True:
				self.dropbox_class.token_class.kill = False
				self.blocking_check_server = True

				# If you are the server
				if self.server_instance == True:
					self.client_socket.close()
					self.server_class.kill_server()
					self.dropbox_class.auto_dismiss = False
					self.ima_used_by_users = {}
					try:
						self.dropbox_class.dbx.files_delete("/Config_Folder/lock_file.txt")
					except:
						pass
				elif self.client_socket == -1:
					self.blocking_check_server = False
					self.dropbox_class.change = False
					self.ima_used_by_users = {}
				else:
					self.dropbox_class.auto_dismiss = False
					self.dropbox_class.change = False
					self.client_socket.close()
					self.ima_used_by_users = {}

				self.dropbox_class.background_load() # Recharge
				return True

			self.dropbox_class.auto_dismiss = True
			self.blocking_check_server = False
			self.change_class.load_class_dropbox.dbx = self.dropbox_class.dbx
			self.change_class.load_class_dropbox.first_time = True
			self.change_class.load_class_dropbox.ids.box_options.clear_widgets()
			# Check if server is on
			self.check_server_operative()

			self.switchid.active = False
			self.using_dropbox = True
			self.change_filter_dropbox = False # Filter control
			self.change_class.using_dropbox = True
			self.change_class.load_path = ""
			self.obj.cu_state = "2D"
			self.images = self.dropbox_class.images_paths

			# Filename and extension
			self.file_name, self.extension = splitext(basename(self.images[0]))
			self.file_path_dropbox = dirname(self.images[0])

			# Obtain URL dropbox image
			self.slider_max.disabled = True
			self.change_restric = True

			try:
				self.img = self.dropbox_class.URL_from_image(self.images[0])
			except:
				self.slider_max.disabled = False
				self.change_restric = False

			self.background_Thread_image_size()

			self.reiniciate_all()
			self.path_change = "" # Can select last folder in filesystem
			self.vol_dimension = True

	# Update class and return keyboard normal control
	def update_class(self, _):

		self.class_name = self.change_class.class_name
		self.class_color = self.change_class.class_color
		self.class_number = self.change_class.classes.get(self.class_name)
		self.load_path = self.change_class.load_path

		if self.mode == "Clasification" and self.change_class.save_clasi == True:
			# Return if not folder selected yet
			if self.disa == True:
				return

			if self.obj.cu_state == "2D":
				json_name = self.obj.path + ".json"
				store = JsonStore(json_name)
				file_name = self.file_name
			elif self.obj.cu_state == "Compress":
				json_name = self.obj.path.replace(".zip", "") + ".json"
				store = JsonStore(json_name)
				file_name = self.zip_name
			else:
				json_name = self.obj.path.replace(self.extension, "") + ".json"
				store = JsonStore(json_name)
				file_name = self.file_name

			# Store the image/class
			store.put(file_name, Class=self.change_class.class_name)

			self.change_class.advice = "Image tag saved!"
			self.change_class.save_clasi = False

			self.create_general_csv(json_name.replace(".json", "_csv_tag_color.txt"))
			return True

		self.write_mode = False
		self.change_class.save_clasi = False

	# Update mode of options
	def update_options(self, _):
		self.mode = self.options_class.mode
		self.borders = self.options_class.borders
		self.dropbox = self.options_class.dropbox

		# Prevent select class while loading csv
		if self.mode == "Clasification":
			self.change_class.clasifi = True
		else:
			self.change_class.clasifi = False

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
		self.switchid.active = False
		self.filter_boolean = False

	# Conect, create and manage server things
	def check_server_operative(self):
		for tries in range(2):
			# Check if still conected to the server
			try:
				self.client_socket.sendall(bytes("p", "utf8"))
				return
			except:
				sleep(0.2)

		# Try to reconect to the server
		try:
			# Connect to server if exists if not create a server
			self.client_socket = self.chat_class.connect_to_server(self.HOST, self.PORT)
			if self.client_socket == -1: # Raise error
				raise Exception("")
			self.ima_used_by_users = {} # Reiniciate current images
			self.background_Thread_creation_listen()
			return
		except:

			# Create server
			self.fire_popup(self.server_loading_class, "")

			t = Thread(target=self.background_server_creation)
			t.daemon = True
			t.start()

	# Background server creation
	def background_server_creation(self):

		# Create server
		self.server_instance = False
		while True:
			# Try to lock the config file in dropbox to prevent some server creation
			try:
				ip_adress = gethostbyname(gethostname())
				compro = self.dropbox_class.lock_file_dropbox(ip_adress)
				if compro == False:
					raise

				self.server_instance = True
				self.HOST = ip_adress
				self.server_class.HOST = ip_adress

				# Create the thread to invoke server creation
				t = Thread(target=self.background_server_listen)
				t.daemon = True
				t.start()
			except:
				# Check new host, loading or internet error
				try:
					for tries in range(2):
						# Update HOST
						metadata, res = self.dropbox_class.dbx.files_download(path="/Config_Folder/lock_file.txt")
						self.HOST = res.content.decode("utf8")

						# Connect to server if exists
						self.client_socket = self.chat_class.connect_to_server(self.HOST, self.PORT)
						if self.client_socket != -1: # Connection works!
							self.ima_used_by_users = {} # Reiniciate current images
							self.background_Thread_creation_listen()
							self.server_loading_class.dismiss() # Dismiss Loading popup
							return

						# Sleep and try in a few seconds	
						sleep(0.2)
					
					# Reiniciate acces to create the server if file is old
					time_date = self.dropbox_class.dbx.files_alpha_get_metadata("/Config_Folder/lock_file.txt")
					now = datetime.now(timezone("UTC")).replace(tzinfo=None)
					creation_time = (now - time_date.server_modified).total_seconds()

					# If file is old delete lcok file
					if creation_time > 10:
						self.dropbox_class.dbx.files_delete("/Config_Folder/lock_file.txt")
				except:
					self.tex_control = "Internet error!"
					return

	# Background checking new messages from server
	def background_server_listen(self):

		self.server_class.create_server(self.HOST, self.PORT) # Host the server

	# Background server listen
	def background_Thread_creation_listen(self):

		# Create the thread to invoke function
		t = Thread(target=self.receive_from_server)
		# Set daemon to true so the thread dies when app is closed
		t.daemon = True
		# Start the thread
		t.start()

	# Background checking new messages from server
	def background_Thread_image_size(self):

		# Create the thread to invoke function
		t = Thread(target=self.back_image_size)
		# Set daemon to true so the thread dies when app is closed
		t.daemon = True
		# Start the thread
		t.start()

	# Update the image in the back
	def back_image_size(self):
		try:
			# Set image size
			file = BytesIO(urlopen(self.img).read())
			self.image_car.size = Image.open(file).size
			self.ori_size = self.image_car.size
		except:
			tex_control = "Image size incorrect!"
			self.slider_max.disabled = False
			self.change_restric = False
		self.slider_max.disabled = False
		self.change_restric = False

	# Reciving messages
	def receive_from_server(self):
		"""Handles receiving of messages."""
		while True:
			try:
				msg = self.client_socket.recv(self.BUFSIZ).decode("utf8")
				# Classify the message
				if msg[0] == "m":
					self.chat_class.receive_from_server(msg[1:])
					self.chat_but.background_normal = "icons/chat_active.png" # Update chat_button state
					self.chat_but.text = "'"
				elif msg[0] == "U":
					pos = msg.rfind("c")
					user = msg[0:pos]
					path = msg[pos + 1: ]
					self.ima_used_by_users[user] = path
				elif msg[0] == "n": # Initial number of users
					self.chat_class.number_users = str(int(msg[1:]))
					self.chat_but.background_normal = "icons/chat_active.png" # Update chat_button state
					self.chat_but.text = "'"
				elif msg[0] == "a": # New or delete user
					self.chat_class.number_users = str(int(self.chat_class.number_users) + int(msg[1:]))
			except:
				# Check if server is on
				if self.blocking_check_server == False:
					self.check_server_operative()
				break

	def changeimage(self, value, value2):
		self.close = False # Reiniciate close line
		if len(self.images) < 1:
			self.img = self.default_path
			self.file_name = basename(self.default_path)
			im_size = Image.open(self.default_path)
			self.image_car.size = im_size.size
			self.ori_size = im_size.size
			self.tex_control = " All Images have masks!"
			self.disa = True
		else:
			# Evaluate the 4 possibilities
			if self.obj.cu_state == "2D":
				if self.using_dropbox == True: # Check if file is in dropbox

					# Check if filter is active and filter list of images
					if self.switchid.active == True:
						self.images = self.copy_images # Reiniciate
						try:
							files_fil = self.dropbox_class.dbx.files_list_folder_continue(self.cursor_filter)
							self.cursor_filter = files_fil.cursor
						except:
							self.tex_control = "Internet error!"
							return

						# Remove images with new masks
						for pos_fil in files_fil.entries:
							new_filter_path = pos_fil.path_display.replace("_masks", "").replace("_mask.png", "")
							self.images = [x for x in self.images if new_filter_path not in x]

						# Filter with current images other users
						self.copy_images = self.images.copy()
						for ima in self.ima_used_by_users.values():
							try:
								self.images.remove(ima)
							except:
								continue

						# If value greater than len list then change
						self.drop_filt = True
						if value >= len(self.images):
							self.slider_max.value = len(self.images) - 1
							self.slider_max.max = len(self.images) - 1
							value = len(self.images) - 1
						else:
							# self.slider_max.value = value
							self.slider_max.max = len(self.images) - 1

						# Send current image to the rest
						self.client_socket.send(bytes("c" + self.images[int(self.slider_max.value)], "utf8"))

					self.drop_filt = False
					img_name_path = self.images[int(value)]
					self.file_name, self.extension = splitext(basename(img_name_path))
					self.file_path_dropbox = dirname(img_name_path)

					# Update image
					self.slider_max.disabled = True
					self.change_restric = True
					try:
						self.img = self.dropbox_class.URL_from_image(img_name_path)
						self.background_Thread_image_size()
					except:
						self.slider_max.disabled = False
						self.change_restric = False
				else:
					self.img = self.images[int(value)]
					self.file_name, self.extension = splitext(basename(self.img))
					im_size = Image.open(self.img)
					self.image_car.size = im_size.size
					self.ori_size = im_size.size
			elif self.obj.cu_state == "Compress":
				bytes_im = BytesIO(self.ima_compress.z_file.read(self.images[int(value)])) # Convert img into bytes
				self.file_name, self.extension = splitext(basename(self.images[int(value)]))
				self.zip_name, _ = splitext(self.images[int(value)])
				self.image_car.texture = CoreImage(bytes_im, ext=self.extension[1:].lower()).texture
				self.image_car.size = Image.open(bytes_im).size
				self.ori_size = Image.open(bytes_im).size
			elif self.obj.cu_state == "Volume":
				self.ima_volume.change_slice(self.images[int(value)], int(value2)) # change the slice position
				self.image_car.texture = self.ima_volume.texture
				self.image_car.size = self.ima_volume.size
				self.ori_size = self.ima_volume.size

				# Update filename with correct dimensions code
				if self.vol_dimension == True:
					self.file_name = self.vol_name + "_" + str(self.images[int(value)])
				else:
					self.file_name = self.vol_name + "_" + str(self.images[int(value)]) + "_" + str(int(value2))
					self.max_dime = self.ima_volume.max_dime

		# Reiniciate factors
		self.x_factor = 0
		self.y_factor = 0
		self.zoom_val = 0

		# Check if filter is actived
		if self.filter_boolean == True and self.using_dropbox == False:
			self.filter_boolean = False # Reiniciate default state
			valu = self.slider_max.value
			self.filter_images(True)
			self.slider_max.value = valu

	# Tree walk relative paths inside a foler
	def tree_walk(self, root_dir):
		file_set = set()

		for dir_, _, files in walk(root_dir):
			for file_name in files:
				rel_dir = relpath(dir_, root_dir)
				if rel_dir != ".":
					rel_file = join(rel_dir, file_name).replace(sep, '/')
				else:
					rel_file = file_name
				file_set.add(rel_file)

		return list(file_set)

	# Functions to filter used images in dir
	def filter_type(self, image):
		# Check if system is Unix and 2d images in local system
		if name_system != "nt" and self.using_dropbox == False and self.obj.cu_state == "2D":
			if image.replace(image[image.rfind("."):], self.exten2)[image.rfind("/") + 1: ] not in self.lista_ima:
				return True
		else:
			if image.replace(image[image.rfind("."):], self.exten2)[image.rfind("\\") + 1: ] not in self.lista_ima:
				return True

	def filter_images(self, state):
		
		# Volume 4 dimension filter disabled
		if self.vol_dimension == False:
			self.switchid.active = False
			return

		if self.mode == "Segmentation" or self.mode == "Instance":
			self.exten = "_masks"
			self.exten2 = "_mask.png"
		else:
			self.exten = "_csv"
			self.exten2 = "_csv.txt"

		if self.obj.cu_state == "2D":
			if self.using_dropbox == True:
				folder_path = self.file_path_dropbox + self.exten
				self.folder_path = folder_path
			else:
				folder_path = self.obj.path + self.exten
		else:
			folder_path = dirname(self.obj.path) + self.exten
			file_name, _ = splitext(basename(self.obj.path))
			file_name, _ = splitext(file_name)
			folder_path = folder_path + "/" + file_name

		# Filter JSON file in classification mode
		if self.mode == "Clasification" and state == True:
			file, _ = splitext(self.obj.path)
			file, _ = splitext(file)
			name = basename(file)
			file = file + ".json"

			filter_store = JsonStore(file)

			self.lista_ima = []
			for item in filter_store:
				self.lista_ima.append(item + "_csv.txt")

			if self.obj.cu_state == "Volume": # Filter volume num
				for x in self.lista_ima:
					x = x.replace(name + "_", "").replace(self.exten2, "")
					try:
						self.images.remove(int(x))
					except:
						continue
			else:
				self.images = list(filter(self.filter_type, self.images))

			# Reiniciate slider values
			self.slider_max.max = len(self.images) - 1
			self.slider_max.value = 0
			return

		# Filter image list
		if self.using_dropbox == True:
			if state == True:
				self.lista_ima = []

				# List mask paths in dropbox folder
				try:
					response = self.dropbox_class.dbx.files_list_folder(folder_path)
				except:
					self.tex_control = "No masks!"
					self.switchid.active = False
					self.filter_boolean = False # Reiniciate default state
					self.disa = False
					return

				self.change_filter_dropbox = True # Control folder change
				self.cursor_filter = response.cursor # Cursor check changes
				for file in response.entries:
					self.lista_ima.append(folder_path.replace(self.exten, "/") + file.name)
				self.ori_images = self.images.copy()
				self.images = list(filter(self.filter_type, self.images)) # Filter images
				
				self.copy_images = self.images.copy()
			else:
				if self.change_filter_dropbox == True:
					self.change_filter_dropbox = False
					self.path_change = ""
					self.images = self.ori_images
					self.disa = False
		elif exists(folder_path):
			if state == True:
				if self.obj.cu_state == "Compress":
					self.lista_ima = self.tree_walk(folder_path)
					self.images = list(filter(self.filter_type, self.images))
				elif self.obj.cu_state == "Volume":
					self.lista_ima = []
					for x in listdir(folder_path):
						x = x.replace(file_name + "_", "").replace(self.exten2, "")
						try:
							self.images.remove(int(x))
						except:
							continue
				else:
					self.lista_ima = listdir(folder_path)
					self.images = list(filter(self.filter_type, self.images))

			else:
				self.path_change = ""
				self.update_path(None)
				self.filter_boolean = False # Reiniciate default state
				self.disa = False
		else:
			self.tex_control = " No masks!"
			self.switchid.active = False
			return

		# Reiniciate slider values
		self.slider_max.max = len(self.images) - 1
		self.slider_max.value = 0

		if self.using_dropbox == True and len(self.images) > 0:
			# Send current image to the rest
			self.client_socket.send(bytes("c" + self.images[int(self.slider_max.value)], "utf8"))

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

	# Rebind keyboard after use textinput
	def rebind_keyboard(self, _):
		# Check if internet fail
		if self.chat_class.check_internet == True:
			pass
		self.chat_class.check_internet = False
		self.chat_class.text_cu_in.focus = False
		self.chat_class.text_cu_in.multiline = True
		self.chat_but.background_normal = "icons/chat_inactive.png" # Update chat_button state
		self.chat_but.text = ""
		self._keyboard.bind(on_key_down=self._on_keyboard_down)

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
				if self.change_restric == False:
					# Change to next image
					if self.slider_max.value < self.slider_max.max:
						if self.filter_boolean == False:
							self.slider_max.value += 1
						else:
							self.slider_max.value -= 1
							self.slider_max.value += 1
			elif keycode[1] == 'left' or keycode[1] == "q":
				if self.change_restric == False:
					# Change to before image
					if self.slider_max.value > self.slider_max.min:
						self.slider_max.value -= 1
			elif keycode[1] == 'w' or 's' or 'a' or 'd':
				self.move_in(keycode[1])
		else:
			self.change_class.advice = "" # Reiniciate advice
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

	# Auxiliar function general class csv save
	def create_general_csv(self, csv_path):
		# Check if load_path is active
			if self.load_path != "":
				csv_path = self.load_path
			else:
				# Copy for prevent user save error
				if exists(csv_path):
					csv_path = csv_path.replace(".txt", "_copy.txt")

			# Write csv files
			if len(self.change_class.classes) > 1:
				with open(csv_path, mode='w') as file:
					file.write("background\t0")
					if self.borders == True:
						file.write("\nborders\t1")
					for item in self.change_class.classes:
						file.write("\n" + item + "\t" + str(self.change_class.classes.get(item)))

	# Background upload tempfile_csv
	def save_csv_dropbox(self):
		with open("temp_files/upload_csv.txt", mode='rb') as file:
			# Upload to dropbox and remove tempfile
			try:
				self.saved_button.disabled = True
				self.dropbox_class.dbx.files_upload(file.read(), self.csv_dropbox_path, mode=WriteMode('overwrite'))
				self.tex_co.color = (1,0,1,1)
				self.tex_control = "Image saved!"
			except:
				self.tex_co.color = (1,0,0,1)
				self.tex_control = "Internet Error!"
				self.saved_button.disabled = True
				
		remove_f("temp_files/upload_csv.txt") # Delete temp file
		self.saved_button.disabled = False

	# Background upload tempfile images_mask
	def save_mask_dropbox(self):
		with open("temp_files/upload_file.png", "rb") as imageFile:
			f = imageFile.read()

		# Upload to dropbox and remove tempfile
		try:
			self.saved_button.disabled = True
			self.dropbox_class.dbx.files_upload(f, self.final_path_dropbox, mode=WriteMode('overwrite'))
			self.tex_co.color = (1,0,1,1)
			self.tex_control = "Image saved!"
		except:
			self.tex_co.color = (1,0,0,1)
			self.tex_control = "Internet Error!"
			self.saved_button.disabled = True

		remove_f("temp_files/upload_file.png") # Delete temp file
		self.saved_button.disabled = False

	# Main function to save mask,csv,etc....
	def save_image(self):

		# Change points to final_points list
		self.new_line(True)
		self.saved_button.disabled = True
		self.tex_co.color = (0,0.4,1,0.9)
		self.tex_control = "saving..."

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
			if len(self.change_class.classes) > 254:
				final_image = Image.new("I", [int(round(self.ori_size[0])),int(round(self.ori_size[1]))])
			else:
				final_image = Image.new("P", [int(round(self.ori_size[0])),int(round(self.ori_size[1]))])
				# Activate color_palette
				final_image.putpalette(color_palette[:256*3])

			draw = ImageDraw.Draw(final_image)

			# Updating last points in list
			self.final_lpoints = [[(x[0] - self.image_car.pos[0], self.image_car.size[1] - (x[1] - self.image_car.pos[1])) for x in y] for y in self.final_points]

			# Drawing lines
			if self.borders == True:
				for i in range(len(self.final_lpoints)):
					draw.polygon(self.final_lpoints[i], fill=self.colors_lis[i], outline=1)
			else:
				for i in range(len(self.final_lpoints)):
					draw.polygon(self.final_lpoints[i], fill=self.colors_lis[i], outline=self.colors_lis[i])

		# Saved final image in mask folder
		if self.obj.cu_state == "2D":
			if self.using_dropbox == True: # Check if file is in dropbox
				self.final_path_dropbox = self.file_path_dropbox + "_masks/" + self.file_name + "_mask.png"
				csv_final_path = "temp_files/upload_csv.txt"
				self.csv_dropbox_path = self.file_path_dropbox + "_csv/" + self.file_name + "_csv.txt"
			else:
				folder_path = self.obj.path + "_masks"
				csv_path = self.obj.path + "_csv_tag_color.txt"
				csv_folder = self.obj.path + "_csv"
				final_path = folder_path + "/" + self.file_name + "_mask.png"
				csv_final_path = csv_folder + "/" + self.file_name + "_csv.txt"
		else:
			folder_path = dirname(self.obj.path) + "_masks"
			csv_folder = dirname(self.obj.path) + "_csv"

			if self.obj.cu_state == "Volume": # Save in new volume folder
				csv_path = folder_path.replace("_masks", "_csv_tag_color.txt")
				folder_path = folder_path + "/" + basename(self.obj.path.replace(self.extension, ""))
				csv_folder = csv_folder + "/" + basename(self.obj.path.replace(self.extension, ""))
				final_path = folder_path + "/" + self.file_name + "_mask.png"
				csv_final_path = csv_folder + "/" + self.file_name + "_csv.txt"
			else:
				csv_path = folder_path.replace("_masks", "/") + basename(self.obj.path.replace(".zip", "_csv_tag_color.txt"))
				final_path = folder_path + "/" + basename(self.obj.path.replace(".zip", "")) + "/" + self.zip_name + "_mask.png"
				csv_final_path = csv_folder + "/" + basename(self.obj.path.replace(".zip", "")) + "/" + self.zip_name + "_csv.txt"
				folder_path = dirname(final_path)
				csv_folder = dirname(csv_final_path)

		# General class value csv
		if self.using_dropbox == False: # Check if file is in dropbox
			self.create_general_csv(csv_path)

		# Reiniciate zoom_val and seeds
		self.zoom_val = 0
			
		# Check if filter is actived
		if self.using_dropbox == False:
			if self.switchid.active == True:
				self.filter_boolean = True

		# Save mask in folder. Create folder if doenst exists
		if self.mode == "Instance" or self.mode == "Segmentation":
			if self.using_dropbox == True: # Check if file is in dropbox
				# Save image to tempfile
				final_image.save("temp_files/upload_file.png")
				# create the thread to invoke function
				t = Thread(target=self.save_mask_dropbox)
				# set daemon to true so the thread dies when app is closed
				t.daemon = True
				# start the thread
				t.start()
				
			else:
				Pathli(folder_path).mkdir(parents=True, exist_ok=True)
				final_image.save(final_path)
				self.tex_co.color = (1,0,1,1)
				self.tex_control = "Image saved!"

		# Save bounding boxes in instance mode
		if self.mode == "Instance" or self.mode == "Bounding_boxes":

			# Create csv image
			if self.using_dropbox == False: # Check if file is in dropbox
				Pathli(csv_folder).mkdir(parents=True, exist_ok=True)
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

					# Write lines in file
					write_line = clas + "\t" + str(round(x)) + "\t" + str(round(y)) + "\t" + str(round(w)) + "\t" + str(round(h)) + "\n"
					file.write(write_line)

			if self.using_dropbox == True: # Check if file is in dropbox
				# create the thread to invoke function
				t = Thread(target=self.save_csv_dropbox)
				# set daemon to true so the thread dies when app is closed
				t.daemon = True
				# start the thread
				t.start()
			else:
				self.tex_co.color = (1,0,1,1)
				self.tex_control = "Image saved!"

class GroundTruthBuilder(App):
	def build(self):
		return LinePlay()


if __name__ == '__main__':

	# Clean temp folder on init
	if exists(getcwd() + '/temp'):
		rmtree(getcwd() + '/temp')
	if exists(getcwd() + '/temp_files'):
		rmtree(getcwd() + '/temp_files')
	Pathli(getcwd() + '/temp').mkdir(parents=True, exist_ok=True)
	Pathli(getcwd() + '/temp_files').mkdir(parents=True, exist_ok=True)
	
	GroundTruthBuilder().run()

	# Clean temp folder on close
	rmtree(getcwd() + '/temp')
	rmtree(getcwd() + '/temp_files')