from dropbox import Dropbox
from dropbox.files import FileMetadata
from os.path import dirname, exists
from os import getcwd
from pathlib import Path as Pathli
from shutil import rmtree
from threading import Thread
from webbrowser import open as open_web

from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.properties import StringProperty
from kivy.storage.jsonstore import JsonStore
from kivy.core.clipboard import Clipboard
from kivy.clock import mainthread

Builder.load_file("Dropbox_link.kv")

# Load token from json file
class LoadToken(Popup):

	advice = StringProperty("")
	store = JsonStore('RootPath.json')
	valid_tokens = []
	delete = "normal"
	token = ""
	running_thread = False

	def __init__(self):
		super(LoadToken, self).__init__()
		# Load Token if exists
		if self.store.exists('CurrentKey'):
			self.dbx = Dropbox(self.store.get('CurrentKey')['token'], timeout=10)
			self.token = self.store.get('CurrentKey')['token']
		else:
			self.dbx = ""

	# Click on button set token
	def button_calback(self, button):

		# Check if delete mode is active
		if self.delete == "down":
			self.ids.box_options.remove_widget(button)
			self.valid_tokens.remove(button.text)
			self.store.delete(button.text)
		else:
			# Check if token changes
			if button.text == self.token:
				self.dismiss()
				return

			# Reiniciate representation
			if exists(getcwd() + '/temp'):
				rmtree(getcwd() + '/temp')
			Pathli(getcwd() + '/temp').mkdir(parents=True, exist_ok=True)
			
			# create the thread to invoke function
			t = Thread(target=self.update_token_value, args=(button,))
			t.daemon = True
			t.start()


	# Change things in background
	def update_token_value(self, button):

		# Preventing more thread creation
		if self.running_thread == True:
			return
		self.running_thread = True
		
		try:
			dbx = Dropbox(button.text, timeout=10)
			response = dbx.files_list_folder("") # Check if token works
			self.dbx = Dropbox(button.text, timeout=10)
			self.store.put('CurrentKey', token=button.text)
			self.token = button.text

			# Dismiss and update
			self.dismiss()
			self.running_thread = False
		except:
			self.advice = "No Internet Conecction or The project does not exist!"
			self.running_thread = False

	# Load tokens from different projects from json file
	def load_tokens_json(self):

		# Remove previus itenms if they existst
		for item in self.ids.box_options.children.copy():
			self.ids.box_options.remove_widget(item)

		# Load tokens if exists
		for key in self.store.keys():
			if key == "RootPath" or key == "CurrentKey":
				continue

			# Add buttons representation from tokens
			button = Button(text=key, size_hint=(1, 1), font_size=14, valign="middle")
			
			# Bind function to the button and properties
			button.bind(on_press=self.button_calback)
			button.background_color = (1,1,1,0.5)
			self.ids.box_options.add_widget(button)
			self.valid_tokens.append(key)

	# Paste token from Paste button
	def paste_token(self):

		self.advice = ""
		# Check if clipboard is a string
		if len(Clipboard.paste()) == 0 or Clipboard.paste() in self.valid_tokens:
			self.advice = "Invalid Token or already used!"
			return
		else:
			# create the thread to invoke function
			t = Thread(target=self.update_paste_token)
			t.daemon = True
			t.start()

	def update_paste_token(self):

		# Preventing more thread creation
		if self.running_thread == True:
			return
		self.running_thread = True

		# Check it tooken works
		try:
			dbx = Dropbox(Clipboard.paste(), timeout=2)
			response = dbx.files_list_folder("") # Check if token works

			# Store the Token
			self.store.put(Clipboard.paste())
			self.store.put('CurrentKey', token=Clipboard.paste())

			# Add buttons representation from tokens
			button = Button(text=Clipboard.paste(), size_hint=(1, 1), font_size=14, valign="middle")
			button.bind(on_press=self.button_calback)
			button.background_color = (1,1,1,0.5)
			self.ids.box_options.add_widget(button)
			self.valid_tokens.append(Clipboard.paste())
			self.running_thread = False
		except:
			self.advice = "No Internet Conecction or Invalid Token!"
			self.running_thread = False


# Class to use dropbox images
class Dropbox_images(Popup):

	rootpath = StringProperty(getcwd().replace("\\", "/", 40) + "/temp") # Virtual Dropbox folder
	token_class = LoadToken()
	folder_list = []
	images_paths = []
	extensions_posi = {".png", ".jpg", ".JPG", ".PNG", ".jpeg", '.jfif', '.JFIF', ".tiff", ".tif", ".BMP", ".bmp", ".TIF", ".TIFF"}
	advice = StringProperty("")
	change = False # Control update process
	change_2 = False
	running_thread = False
	running_thread2 = False
	problem = False
	path = ""
	dbx = ""

	# Check if file is a folder
	def isFile(self, dropboxMeta):
		return isinstance(dropboxMeta, FileMetadata)

	# Fuction to load things in background
	def background_load(self):
		self.dbx = self.token_class.dbx
		self.advice = "" # Reiniciate advice value
		self.change = False

		if self.dbx == "":
			self.advice = "Set token!"
			return

		# Preventing more thread creation
		if self.running_thread == True:
			return
		self.running_thread = True
		self.advice_label.color = (0,0.4,1,0.9)
		self.advice = "Loading Folders..."

		# create the thread to invoke function
		t = Thread(target=self.obtain_folders_structure)
		# set daemon to true so the thread dies when app is closed
		t.daemon = True
		# start the thread
		t.start()

	# Fuction to load things in background
	def background_final_files(self):

		path = self.filecho.path
		self.change = False
		self.sele_button.disabled = True
		
		# Preventing more thread creation
		if self.running_thread2 == True:
			self.sele_button.disabled = True
			return
			
		self.sele_button.disabled = True
		self.running_thread2 = True
		self.auto_dismiss = False
		self.advice_label.color = (0,0.4,1,0.9)
		self.advice_label.text = "Updating files..."
		self.path = path

		# create the thread to invoke function
		t = Thread(target=self.update_images_path)
		# set daemon to true so the thread dies when app is closed
		t.daemon = True
		# start the thread
		t.start()

	# Main thread update operations for thread safe
	@mainthread
	def update_ui(self):
		self.filecho._update_files()

	@mainthread
	def pop_dismiss(self):
		self.dismiss()

	# Create the Filechooser grab folders
	def obtain_folders_structure(self):

		try:
			folder_list = self.folder_list.copy()
			self.folder_list = []
			response = self.dbx.files_list_folder("", recursive=True) # Dropbox folder list
		except:
			self.advice_label.color = (1,0,0,1)
			self.advice = "No Internet Conecction or The token is no longer active!"
			self.running_thread = False
			return

		for file in response.entries:
			if self.isFile(file) == True:
				break
			else:
				if file.path_display not in self.folder_list and file.name.endswith(('_csv', '_CSV', '_masks', 'Config_Folder')) == False:
					self.folder_list.append(file.path_display)
					Pathli(self.rootpath + file.path_display).mkdir(parents=True, exist_ok=True)

		# Just update view when new folder
		if folder_list == self.folder_list and self.problem == False:
			self.running_thread = False
			self.advice = ""
			return

		self.problem = False
		self.advice = "Loading Files..."
		self.obtain_files_paths()

	# Create the Filechooser files representation grab and obtain files in dropbox
	def obtain_files_paths(self):
		for folder in self.folder_list:

			# Handle internet conecction error
			try:
				response = self.dbx.files_list_folder(folder)
			except:
				self.advice_label.color = (1,0,0,1)
				self.advice = "Internet Connection Problem!"
				self.running_thread = False
				self.problem = True
				return

			num_files = 0
			for file in response.entries:
				if self.isFile(file) == True and file.name[file.name.rfind("."): ] in self.extensions_posi:

					# Create files representation
					if num_files < 5:
						# Create representation file
						f = open(self.rootpath + file.path_display, "wb")
						f.close()

						num_files += 1
					elif num_files == 5:
						f = open(self.rootpath + dirname(file.path_display) + "/zzz.......jpg", "wb")
						f.close()
						num_files += 1
					else:
						break

			self.advice = ""
			self.running_thread = False
			self.update_ui() # Update view in th main thread

	# Dismiss function update images path
	def update_images_path(self):
		search_path = self.path.replace("\\", "/", 40).replace(self.rootpath, "")
		self.images_paths = []

		# Handle internet conecction error
		try:
			response = self.dbx.files_list_folder(search_path)
		except:
			self.advice_label.color = (1,0,0,1)
			self.advice = "Internet Connection Problem!"
			self.auto_dismiss = True
			self.sele_button.disabled = False
			self.running_thread2 = False
			return

		self.change = True
		self.pop_dismiss()
		for file in response.entries:
			if self.isFile(file) == True and file.name[file.name.rfind("."): ] in self.extensions_posi:
				self.images_paths.append(file.path_display)

		self.advice = ""
		self.auto_dismiss = True
		self.running_thread2 = False

	# Obtain URL from image path for asyn load
	def URL_from_image(self, path):
		URL = self.dbx.files_get_temporary_link(path)
		return URL.link

	# Open webrowser app dropbox
	def open_web_dropbox(self):
		open_web('https://www.dropbox.com/login?cont=https%3A%2F%2Fwww.dropbox.com%2Fdevelopers%2Fapps%2Fcreate', new=2)

	# Fire set token popup
	def fire_pop(self):
		self.token_class.load_tokens_json()
		self.token_class.bind(on_dismiss=self.update_token)
		self.token_class.open()

	# Update token used for access dropbox project folder
	def update_token(self, _):
		# Charge Token asociated with app folder
		self.dbx = self.token_class.dbx
		self.token_class.advice = ""
		self.change = True
		self.background_load()


# FIleChooser load/save csv
class LoadCsvDopbox(Popup):
	load_path = ""
	dic_classes = {}
	files_list = []
	advice = StringProperty("")
	running_thread = False
	first_time = True
	file_name = ""
	dbx = ""

	# Fuction to load things in background
	def background_load(self):
		self.advice = "" # Reiniciate advice value
		
		# Preventing more thread creation
		if self.running_thread == True:
			return
		self.running_thread = True
		self.advice_label.color = (0,0.4,1,0.9)
		self.advice = "Loading Files..."

		# create the thread to invoke function
		t = Thread(target=self.add_csvfile_representation)
		# set daemon to true so the thread dies when app is closed
		t.daemon = True
		# start the thread
		t.start()

	# Fuction to load things in background
	def background_update_classes(self):
		
		# Preventing more thread creation
		if self.running_thread == True:
			return
		self.running_thread = True
		# Disabled button while updating
		for button in self.ids.box_options.children:
			button.disabled = True
		self.auto_dismiss = False
		self.advice_label.color = (1,0.4,0,0.9)
		self.advice = "Updating file..."
		# create the thread to invoke function
		t = Thread(target=self.update_classes)
		# set daemon to true so the thread dies when app is closed
		t.daemon = True
		# start the thread
		t.start()

	def button_calback(self, button):

		self.file_name = button.text
		self.background_update_classes()

	# Update local copy base on server side
	def update_classes(self):
		# Donwload local copy of classes_csv
		with open("temp_files/general_csv.txt", "wb") as f:
			try:
				metadata, res = self.dbx.files_download(path="/Classes_CSV/" + self.file_name)
			except:
				self.advice_label.color = (1,0,0,1)
				self.advice = "Internet Connection Problem!"
				# Active buttons
				for button in self.ids.box_options.children:
					button.disabled = False
				self.auto_dismiss = True
				self.running_thread = False
				return
			f.write(res.content)

		# Read CSV and update dictionary
		self.dic_classes = {}
		with open("temp_files/general_csv.txt", mode='r') as file:
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
			# Active buttons
			for button in self.ids.box_options.children:
				button.disabled = False
			self.auto_dismiss = True
			self.running_thread = False
			return

		self.load_path = "/Classes_CSV/" + self.file_name
		self.dismiss()
		# Active buttons
		for button in self.ids.box_options.children:
			button.disabled = False
		self.auto_dismiss = True
		self.running_thread = False

	def add_csvfile_representation(self):
		if self.first_time == True:
			# Handle internet conecction error
			try:
				# Explore possibilities and save cursor
				response = self.dbx.files_list_folder("/Classes_CSV")
				self.cursor = response.cursor
			except:
				self.advice_label.color = (1,0,0,1)
				self.advice = "Internet Connection Problem!"
				self.running_thread = False
				return

			for entry in response.entries:
				button = Button(text=entry.name, size_hint=(1, 1), font_size=20, valign="middle")
				# Bind function to the button and properties
				button.bind(on_press=self.button_calback)
				button.background_color = (1,1,1,0.5)
				self.ids.box_options.add_widget(button)

			self.first_time = False
		else:
			# Handle internet conecction error
			try:
				response = self.dbx.files_list_folder_continue(self.cursor)
				self.cursor = response.cursor
			except:
				self.advice_label.color = (1,0,0,1)
				self.advice = "Internet Connection Problem!"
				self.running_thread = False
				return

			for entry in response.entries:
				no_add = False
				# Check if file already exist in current buttons
				for button in self.ids.box_options.children.copy():
					if button.text == entry.name:
						self.ids.box_options.remove_widget(button)
						no_add = True
						break
					else:
						continue

				# Add new files in folder
				if no_add == False:
					button = Button(text=entry.name, size_hint=(1, 1), font_size=20, valign="middle")
					# Bind function to the button and properties
					button.bind(on_press=self.button_calback)
					button.background_color = (1,1,1,0.5)
					self.ids.box_options.add_widget(button)

		self.advice = ""
		self.running_thread = False