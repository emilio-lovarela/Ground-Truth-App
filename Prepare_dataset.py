import glob, os
from PIL import Image
import sys

directory = "C:/Users/usuario/Documents/Master_bioinformatica/TFM/ImagenesResize/Cubos_Triton/"
train_pro = 0.8

# Prevent train_pro errors
if train_pro < 0.1 or train_pro > 1:
	print("error! Must be a number in range 0.1 - 1")

val_pro = 1 - train_pro

# Function to obtain absolutepaths of masks in the folder.
# Meter las extensiones!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
def absoluteFilesPaths(directory):
	lista = []
	for item in glob.glob(directory + "*_masks"):
		lista.extend(glob.glob(item + "\\" + "*"))

	return lista


# Create data tree if doesnt exist or filter when exist
def filter_files(directory):
	data_path = os.path.dirname(directory.rstrip("/")) + "/data"

	if os.path.exists(data_path) == False:
		for pha in ["train", "val"]:
			os.makedirs((os.path.dirname(directory.rstrip("/")) + "\\data\\" + pha + "\\images").replace("/", "\\", 20))
			os.makedirs((os.path.dirname(directory.rstrip("/")) + "\\data\\" + pha + "\\masks").replace("/", "\\", 20))
	else:
		filter_list = []
		for pha in ["train", "val"]:
			filter_list.extend(os.listdir(data_path + "/" + pha + "/masks"))

		return filter_list


# List with masks in folders and list with masks in data folder
train_set = set(absoluteFilesPaths(directory))
filter_set = set(filter_files(directory))

# Filter masks with masks in data
for value in train_set.copy():
	base_value = os.path.basename(value)
	if base_value in filter_set:
		train_set.remove(value)

# Exit if train_set is empty
if len(train_set) == 0:
	print("Doesn't exist new masks to add!")
	sys.exit() # Cambiar por returnnnnnnnnnnnnnnnnn de funcion

# Random selection images to val
if val_pro == 0:
	data = [train_set]
else:
	n_val = round(len(train_set) * val_pro) # Number of val images
	val_set = set()

	# Random selection
	for a in range(0,n_val):
		val_set.add(train_set.pop())

	data = [train_set, val_set]
	
# Create list of train and val for images
i = 0
pha = "train"

for phase in data:
	if i > 0:
		pha = "val"
	for file in phase:
		cu_path = os.path.dirname(file).replace("_masks", "")
		if os.path.exists(cu_path) == True:
			fi_file = cu_path + "\\" + os.path.basename(file).replace("_mask.png", ".jpg") # Poner para todas las extensiones
			if os.path.exists(fi_file) == True:

				# Save image and mask in folders
				image_file = Image.open(fi_file)
				mask_file = Image.open(file)
				image_file.save(os.path.dirname(directory.rstrip("/")) + "\\data\\" + pha + "\\images\\" + os.path.basename(fi_file))
				mask_file.save(os.path.dirname(directory.rstrip("/")) + "\\data\\" + pha + "\\masks\\" + os.path.basename(file))
			else:
				print("file doesnt exist!")
				break
		else:
			print("folder doesnt exist!")
			filter(lambda x: cu_path not in x, data[0]) # Tryyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy
			filter(lambda x: cu_path not in x, data[1])
	i += 1