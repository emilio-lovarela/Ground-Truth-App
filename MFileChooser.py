from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.storage.jsonstore import JsonStore

from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.textinput import TextInput

from os.path import isdir, exists, isfile

Builder.load_file("MFileChooser.kv")

class MFileChooser(Popup):

	path = StringProperty('')
	RootPath = StringProperty('')
	Invalid_Path = StringProperty('')
	idtxt = ObjectProperty()
	store = JsonStore('RootPath.json')

	def __init__(self):
		super(MFileChooser, self).__init__()
		# Load Rootpath if exists
		if self.store.exists('RootPath'):
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
			self.idtxt.text = ''

class PopupButton(Button):

	def fire_popup(self, pops):
		pops.open()