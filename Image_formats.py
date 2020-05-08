from kivy.app import App
from kivy.uix.image import Image
from kivy.graphics.texture import Texture
from numpy import uint8, flipud
from zipfile import ZipFile
from nibabel import load

# Class to extract a numpy image from a volume and convert to a texture
class Volume_image(Image):

	def __init__(self, file_path):
		super(Volume_image, self).__init__()

		# Load volume 3d or 4d and select initial image
		self.volume_nii = load(file_path)
		if len(self.volume_nii.shape) == 3:
			img_base = self.volume_nii.get_fdata()[:,0,:]
			img_base *= 255.0/img_base.max() # Normalize values range
			img_base = img_base.astype(uint8)
			self.dimension = True
			self.max_dime = 0
		else:
			img_base = self.volume_nii.get_fdata()[:,0,:,0]
			img_base *= 255.0/img_base.max() # Normalize values range
			img_base = img_base.astype(uint8)
			self.dimension = False
			self.max_dime = self.volume_nii.shape[3] - 1

		self.img = flipud(img_base)

		self.size = (self.img.shape[0], self.img.shape[1])
		self.lenght = self.volume_nii.shape[1]

		self.TransformToTexture()

	def TransformToTexture(self):
		buf = self.img.tostring()
		image_texture = Texture.create(size=(self.img.shape[1], self.img.shape[0]), colorfmt='luminance')
		image_texture.blit_buffer(buf, colorfmt='luminance', bufferfmt='ubyte')

		self.texture = image_texture

	def change_slice(self, val, val2):
		if len(self.volume_nii.shape) == 3:
			img_base = self.volume_nii.get_fdata()[:,val,:]
			img_base *= 255.0/img_base.max() # Normalize values range
			img_base = img_base.astype(uint8)
		else:
			img_base = self.volume_nii.get_fdata()[:,val,:,val2]
			img_base *= 255.0/img_base.max() # Normalize values range
			img_base = img_base.astype(uint8)

		self.img = flipud(img_base)

		self.size = (self.img.shape[0], self.img.shape[1])
		self.TransformToTexture()

# Class to extract a PIL image from a zip
class Compress_image():

	def __init__(self, file_path):

		# List images in the compress file
		self.z_file = ZipFile(file_path, mode="r")
		name_li = ZipFile.namelist(self.z_file)
		self.images_names = [i for i in name_li if i.lower().endswith(('.png', '.jpg', '.jpeg', '*.jfif', ".tiff", ".tif", ".bmp"))] # Filter list of images