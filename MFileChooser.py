from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.storage.jsonstore import JsonStore

from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.textinput import TextInput
import os

from os.path import join, isdir, exists

Builder.load_file("MFileChooser.kv")

class MFileChooser(Popup):

	Path = StringProperty()
	RootPath = StringProperty('')
	Invalid_Path = StringProperty('')
	idtxt = ObjectProperty()

	def __init__(self):
		super(MFileChooser, self).__init__()
		# Load Rootpath if exists
		store = JsonStore('RootPath.json')
		if store.exists('RootPath'):
			self.RootPath = store.get('RootPath')['Path']

	def is_dir(self, directory, filename):
		return join(directory, filename)

	def path_exist(self, file_path):
		if not os.path.exists(file_path):
			self.Invalid_Path = "Invalid Path!"

		else:
			# Store the value
			store = JsonStore('RootPath.json')
			store.put('RootPath', Path=file_path)

			# Update RootPath
			self.RootPath = file_path
			self.Invalid_Path = "Root Changed!"
			self.idtxt.text = ''

class PopupButton(Button):

	def fire_popup(self, obj):
		pops = obj
		pops.open()

class Test(BoxLayout):
	obj = MFileChooser()
	pass

class MyApp(App):
	def build(self):
		return Test()

if __name__ == '__main__':
	MyApp().run()