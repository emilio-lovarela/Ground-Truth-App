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
		if self.filecho.selection[0].lower().endswith(('.nii', '.nii.gz')) == True:
			self.path = self.filecho.selection[0]
			self.Invalid_Path = ''
			self.cu_state = "Volume"
			self.dismiss()
		elif self.filecho.selection[0].lower().endswith(('.zip')) == True:
			self.path = self.filecho.selection[0]
			self.Invalid_Path = ''
			self.cu_state = "Compress"
			self.dismiss()