from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.uix.button import Button

from kivy.properties import StringProperty

from os.path import join, isdir

Builder.load_file("MFileChooser.kv")

class MFileChooser(Popup):

	Path = StringProperty()

	def is_dir(self, directory, filename):
		return join(directory, filename)

class SimpleButton(Button):
	text = "Select Images Folder!"
	def fire_popup(self):
		pops=MFileChooser()
		pops.open()


class MyApp(App):
	def build(self):
		return SimpleButton()

if __name__ == '__main__':
	MyApp().run()