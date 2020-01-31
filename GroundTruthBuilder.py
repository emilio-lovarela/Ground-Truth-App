import glob, os
from PIL import Image, ImageDraw
from math import cos, sin
from kivy.app import App
from kivy.properties import NumericProperty, ListProperty, \
        BooleanProperty, StringProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.graphics import Line
from kivy.config import Config

Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

# Builder.load_file("GroundTruthBuilder.kv")

# Path images
# path = ""
images = []

# Images list names
images = glob.glob(r'images/*.jpg') + glob.glob(r'images/*.png')

# Create folder for saves masks
if not os.path.exists('masks'):
    os.makedirs('masks')

class LinePlay(BoxLayout):

	alpha_controlline = NumericProperty(1.0)
	close = BooleanProperty(False)
	points = ListProperty([])
	lpoints = ListProperty([])
	final_points = ListProperty([])
	final_lpoints = ListProperty([])
	LImages = len(images) - 1
	img = StringProperty(images[0])
	image_car = ObjectProperty()
	tex_control = StringProperty("")
	
	def changeimage(self, value):
		self.close = False # Reiniciate close line
		self.img = images[int(value)]

	def on_touch_down(self, touch):
		if super(LinePlay, self).on_touch_down(touch):
			return True
		touch.grab(self)
		self.points.append(touch.pos)
		self.lpoints.append((touch.x - self.image_car.pos[0], self.image_car.size[1] - (touch.y - self.image_car.pos[1])))
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

	def save_image(self, size, pos):
		# Generated mask
		final_image = Image.new("RGB", [int(round(size[0])),int(round(size[1]))])
		draw = ImageDraw.Draw(final_image)

		# Drawing lines
		if not self.lpoints or len(self.lpoints) == 1:
			for i in self.final_lpoints:
				draw.line(i, fill="White", width=1)
		else:
			for i in self.final_lpoints:
				draw.line(i, fill="White", width=1)

			# Close line
			if self.close == True:
				draw.line(self.lpoints + [self.lpoints[0]], fill="White", width=1)
			else:
				draw.line(self.lpoints, fill="White", width=1)


		# Saved final image in mask folder
		filename = "masks\\" + str(self.img).replace(".jpg", "mask.jpg").replace(".png", "mask.png").replace("images\\", "")
		final_image.save(filename)
		# print("size: ", size, " pos: ", pos, self.points, self.lpoints)

	def new_line(self):
		# Handling empty list error
		if not self.points:
			self.close = False # Reiniciate close line
			return

		# Final point list
		if self.close == True:
			self.points.append(self.points[0])
			self.lpoints.append(self.lpoints[0])
		
		self.final_points.append(self.points)
		self.final_lpoints.append(self.lpoints)
		self.points = []
		self.lpoints = []
		self.close = False # Reiniciate close line

		for i in range(0,len(self.final_points)):
			with self.canvas:
				Line(points=self.final_points[i], group='Lines')


class GroundTruthBuilder(App):
	def build(self):
		return LinePlay()


if __name__ == '__main__':
    GroundTruthBuilder().run()