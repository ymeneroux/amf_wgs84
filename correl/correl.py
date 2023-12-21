import os
import cv2
import sys
import numpy as np
import scipy.signal
import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET



# ------------------------------------------------------------------------
# USAGE: python correl.py mesures_2d.xml directory_of_images <factor>
# ------------------------------------------------------------------------


input_path_images  = sys.argv[2]   # Dossier des images
input_path_measure = sys.argv[1]   # Chemin fichier xml des mesures 2D


# ------------------------------------------------------------------------
factor_window = 1.0              # Facteur fenetre de correlation
default_block_size = 100         # Valeur par defaut fenetre correlation
default_out_dir = "Out_correl"   # Repertoire de sortie par defaut
# ------------------------------------------------------------------------


frsz = 10

if (len(sys.argv) > 3):
	factor_window = (float)(sys.argv[3]) 
if (len(sys.argv) > 4):
	default_out_dir = (sys.argv[4])

if (os.path.isdir(default_out_dir)):
	answer=""
	answer = "y"  # !!!!!!!
	while not ((answer=="y") or (answer=="n")):
		answer = input("Directory ["+default_out_dir+"] already exists. Continue? [y/n]  ")
		if (answer=="y"):
			break
		else:
			sys.exit()
else:
	os.mkdir(default_out_dir)
	os.mkdir(default_out_dir+"/vignets")
	os.mkdir(default_out_dir+"/vignets/master")

POINTS_NAME     = []
POINTS_X        = []
POINTS_Y        = []
BLOCK_SIZE      = []
BLOCK_SIZE_DEF  = []

# -----------------------------------------------------------------
# Fonctions utilitaires
# -----------------------------------------------------------------
def upsample(image, factor=frsz, method=cv2.INTER_LINEAR):
	return cv2.resize(image, (factor*image.shape[0], factor*image.shape[1]), interpolation=method)

# -----------------------------------------------------------------
# Lecture des coordonnees de l'image initiale
# -----------------------------------------------------------------

tree = ET.parse(input_path_measure)
root = tree.getroot()


for set_mesures in root.findall('MesureAppuiFlottant1Im'):
	print("----------------------------------------------------------------")
	name_image_init = set_mesures.findall('NameIm')[0].text
	full_name_image_init = input_path_images+"/"+name_image_init
	print(name_image_init, "-> Master image")
	print("----------------------------------------------------------------")
	for point in set_mesures.findall('OneMesureAF1I'):
		coords          = point.findall('PtIm')[0].text.split(" ")
		POINTS_NAME.append(point.findall('NamePt')[0].text)
		POINTS_X.append((float)(coords[0]))
		POINTS_Y.append((float)(coords[1]))
		list_block_size = point.findall('BlockSize')
		BLOCK_SIZE_DEF.append((len(list_block_size) > 0))
		if (BLOCK_SIZE_DEF[-1]):
			BLOCK_SIZE.append(factor_window*(float)(list_block_size[0].text))
		else:
			BLOCK_SIZE.append(factor_window*default_block_size) 
		print("["+POINTS_NAME[-1]+"]", '{:8.3f}'.format(POINTS_X[-1]), '{:8.3f}'.format(POINTS_Y[-1]), '{:6.1f}'.format(BLOCK_SIZE[-1]))



# -----------------------------------------------------------------
# Recuperation des vignettes dans l'image initiale
# -----------------------------------------------------------------

LLX = []
LLY = []
URX = []
URY = []

VIGNETS = []

img_init = cv2.imread(full_name_image_init) 
img_init_original = img_init.copy()

NX = img_init_original.shape[0]
NY = img_init_original.shape[1]


for i in range(len(POINTS_NAME)):
	ll_px = ((int)(POINTS_X[i]-BLOCK_SIZE[i]/2+0.5), (int)(POINTS_Y[i]-BLOCK_SIZE[i]/2+0.5))
	ur_px = ((int)(POINTS_X[i]+BLOCK_SIZE[i]/2+0.5), (int)(POINTS_Y[i]+BLOCK_SIZE[i]/2+0.5))
	LLX.append(max(min(ll_px[0], NY), 0))
	LLY.append(max(min(ll_px[1], NX), 0))
	URX.append(max(min(ur_px[0], NY), 0))
	URY.append(max(min(ur_px[1], NX), 0))
	
	color = (0, 0, 255)
	if (BLOCK_SIZE_DEF[i]):
		color = (0, 255, 0)
	cv2.rectangle(img_init, (LLX[-1], LLY[-1]), (URX[-1],URY[-1]), color , 2) 

	crop = img_init_original[LLY[-1]:URY[-1], LLX[-1]:URX[-1], :]
	VIGNETS.append(upsample(crop)[:,:,0])
	cv2.imwrite(default_out_dir+"/vignets/master/"+POINTS_NAME[i]+".png", crop) 

cv2.imwrite(default_out_dir+"/initImgWithVignets.png", img_init)

# -----------------------------------------------------------------
# Creation repertoire vignettes
# -----------------------------------------------------------------
for name in POINTS_NAME:
	path_dir_vignette = default_out_dir + "/vignets/" + name
	if not (os.path.isdir(path_dir_vignette)):
		os.mkdir(path_dir_vignette)

# -----------------------------------------------------------------
# Correlation par image
# -----------------------------------------------------------------
counter = 0;
print("----------------------------------------------------------------")
for f in sorted(os.listdir(input_path_images)):
	if (f == name_image_init):
		continue
	counter += 1
	#print("----------------------------------------------------------------")
	print(f, "-> Image "+'{:04d}'.format(counter))
	#print("----------------------------------------------------------------")
	img_current = cv2.imread(input_path_images+"/"+f) 
	for i in range(len(POINTS_NAME)):
	#for i in range(1,2):
		crop = img_current[LLY[i]:URY[i], LLX[i]:URX[i], :]
		center_init = ((URX[i]-LLX[i])/2.0, (URY[i]-LLY[i])/2.0)
		crop_us = upsample(crop)[:,:,0]
		corr = scipy.signal.fftconvolve(crop_us, VIGNETS[i][::-1,::-1], mode='same')
		corr = np.power(corr, 5); corr = corr/np.max(corr)*255
		pos_max = np.unravel_index(np.argmax(corr), corr.shape)
		
		dx = pos_max[0]/frsz - center_init[0]
		dy = pos_max[1]/frsz - center_init[1]
		
		print("["+POINTS_NAME[i]+"]", '{:7.3f}'.format(dx), '{:7.3f}'.format(dy))
		
		crop_us_output = upsample(crop, method=cv2.INTER_NEAREST)
			
		center = (center_init[0]+dy, center_init[1]+dx)
		
		cv2.circle(crop_us_output, (int(frsz*center[0])+5, int(frsz*center[1])+5), frsz, (0,0,255), 2)
		 
		out_file = default_out_dir+"/vignets/"+POINTS_NAME[i]+"/"+f.split('.')[0]+"_"+POINTS_NAME[i]+".png"

		cv2.imwrite(out_file, crop_us_output) 
		
		#plt.imshow(corr, cmap='gray')
		#plt.show() 
	#break 
		
print("----------------------------------------------------------------")
#plt.imshow(VIGNETS[0], cmap='gray')
#plt.show()


