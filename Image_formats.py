from kivy.app import App
from kivy.uix.image import Image
from kivy.graphics.texture import Texture
import numpy as np
from zipfile import ZipFile
import nibabel as nib
import cv2

# Class to extract a numpy image from a volume and convert to a texture
class Volume_image(Image):

	def __init__(self, file_path):
		super(Volume_image, self).__init__()

		# Load volume 3d or 4d and select initial image
		self.volume_nii = nib.load(file_path)
		if len(self.volume_nii.shape) == 3:
			img_base = self.volume_nii.get_fdata()[:,0,:].astype(np.uint8)
			self.dimension = True
			self.max_dime = 0
		else:
			img_base = self.volume_nii.get_fdata()[:,0,:,0].astype(np.uint8)
			self.dimension = False
			self.max_dime = self.volume_nii.shape[3] - 1

		self.img = cv2.cvtColor(img_base, cv2.COLOR_GRAY2BGR)

		self.size = (self.img.shape[0], self.img.shape[1])
		self.lenght = self.volume_nii.shape[1]

		self.TransformToTexture()

	def TransformToTexture(self):
		buf1 = cv2.flip(self.img, 0)
		buf = buf1.tostring()
		image_texture = Texture.create(size=(self.img.shape[1], self.img.shape[0]), colorfmt='bgr')
		image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')

		self.texture = image_texture

	def change_slice(self, val, val2):
		if len(self.volume_nii.shape) == 3:
			img_base = self.volume_nii.get_fdata()[:,val,:].astype(np.uint8)
		else:
			img_base = self.volume_nii.get_fdata()[:,val,:,val2].astype(np.uint8)

		self.img = cv2.cvtColor(img_base, cv2.COLOR_GRAY2BGR)

		self.size = (self.img.shape[0], self.img.shape[1])
		self.TransformToTexture()

# Class to extract a PIL image from a zip
class Compress_image():

	def __init__(self, file_path):

		# List images in the compress file
		self.z_file = ZipFile(file_path, mode="r")
		name_li = ZipFile.namelist(self.z_file)
		self.images_names = [i for i in name_li if i.lower().endswith(('.png', '.jpg', '.jpeg', '*.jfif', ".tiff", ".tif", ".bmp"))] # Filter list of images