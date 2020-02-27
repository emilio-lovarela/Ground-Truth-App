import glob, os
from PIL import Image

directory = "C:/Users/usuario/Documents/Master bioinformatica/TFM/ImagenesResize/Cubos Tritón/"
train_pro = 0.8

# Prevent train_pro errors
if train_pro < 0.1:
	train_pro = 0.1
elif train_pro > 1 and train_pro <= 100:
	train_pro = train_pro / 100
elif train_pro > 100:
	print("error!")

val_pro = 1 - train_pro

# Function to obtain absolutepaths of masks in the folder.
# Meter las extensiones!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
def absoluteFilesPaths(directory):
	lista = []
	for item in glob.glob(directory + "*_masks"):
		lista.extend(glob.glob(item + "\\" + "*"))
	return lista

# List with mask in folders. Separate in train and val.
train_set = set(absoluteFilesPaths(directory))

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

# Create data tree if doesnt exist
if os.path.exists(os.path.dirname(directory.rstrip("/")) + "\\data") == False:
	for pha in ["train", "val"]:
		os.makedirs((os.path.dirname(directory.rstrip("/")) + "\\data\\" + pha + "\\images").replace("/", "\\", 20))
		os.makedirs((os.path.dirname(directory.rstrip("/")) + "\\data\\" + pha + "\\masks").replace("/", "\\", 20))
	
# Create list of train and val for images
i = 0
pha = "train"

for phase in data:
	if i > 0:
		pha = "val"
	for file in phase:
		cu_path = os.path.dirname(file).replace("_masks", "")
		if os.path.exists(cu_path) == True:
			fi_file = cu_path + "\\" + os.path.basename(file).replace("_mask", "")
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