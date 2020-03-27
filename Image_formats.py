from kivy.app import App
from kivy.uix.image import Image
from kivy.graphics.texture import Texture
import numpy as np
from zipfile import ZipFile

# Class to extract a numpy image from a volume and convert to a texture
class Volume_image(Image):

	def __init__(self, **kwargs):
		super(Volume_image,  self).__init__(**kwargs)

		self.img = cv2.imread('Trompeteo/cinta.jpg')

		self.size = (self.img.shape[0], self.img.shape[1])
		self.pos = (0, 0)

		self.TransformToTexture()

	def TransformToTexture(self):
		buf1 = cv2.flip(self.img, 0)
		buf = buf1.tostring()
		image_texture = Texture.create(size=(self.img.shape[1], self.img.shape[0]), colorfmt='bgr')
		image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')

		self.texture = image_texture

	def process(self):
		self.TransformToTexture()

# Class to extract a PIL image from a zip
class Compress_image():

	def __init__(self, file_path):

		# List images in the compress file
		self.z_file = ZipFile(file_path, mode="r")
		name_li = ZipFile.namelist(self.z_file)
		self.images_names = [i for i in name_li if i.lower().endswith(('.png', '.jpg', '.jpeg', "*.tiff", "*.BMP"))]


# from PIL import Image
# from io import BytesIO
# ruta = "images/images_comp.zip"
# z_file = ZipFile(ruta, mode="r")

# name_li = ZipFile.namelist(z_file)
# print(name_li)
# print(z_file.filename)

# images_names = [i for i in name_li if i.lower().endswith(('.png', '.jpg', '.jpeg', "*.tiff", "*.BMP"))]
# print(images_names)


# Obtain Image file
# data = z_file.read(images_names[slider])
# dataEnc = BytesIO(data)
# img = Image.open(dataEnc)