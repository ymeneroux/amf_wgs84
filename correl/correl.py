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


frsz = 5
margin = 20

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
def upsample(image, factor=10, method=cv2.INTER_CUBIC):
	return cv2.resize(image, (factor*image.shape[0], factor*image.shape[1]), interpolation=method)
	
	
def phaseCorrelation(image, vignette):
	corr = scipy.signal.fftconvolve(image, vignette[::-1,::-1], mode='valid')	
	pos_max = np.unravel_index(np.argmax(corr), corr.shape)
	return [pos_max[1], pos_max[0], np.max(corr)] 


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
	VIGNETS.append(upsample(crop, factor=frsz)[:,:,0])
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
# Stockage des valeurs de référence
# -----------------------------------------------------------------
REF_X = []
REF_Y = []
print("----------------------------------------------------------------")
print("Computing reference shifts...")
print("----------------------------------------------------------------")
for i in range(len(POINTS_NAME)):
	img_current = cv2.imread(input_path_images + "/" + name_image_init) 
	crop = img_current[LLY[i]-margin:URY[i]+margin, LLX[i]-margin:URX[i]+margin, :]
	crop_us = upsample(crop, factor=frsz)[:,:,0]
	CORREL = phaseCorrelation(crop_us, VIGNETS[i])
	dx  = CORREL[0]/frsz-margin
	dy  = CORREL[1]/frsz-margin
	REF_X.append(dx)
	REF_Y.append(dy)
	print("REF FOR ["+POINTS_NAME[i]+"]", '{:7.3f}'.format(dx), '{:7.3f}'.format(dy))
	



# -----------------------------------------------------------------
# Correlation par image
# -----------------------------------------------------------------
counter = 0;
print("----------------------------------------------------------------")
for f in sorted(os.listdir(input_path_images)):
	if (f == name_image_init):
		continue
	counter += 1
	print("----------------------------------------------------------------")
	print(f, "-> Image "+'{:04d}'.format(counter))
	print("----------------------------------------------------------------")
	img_current = cv2.imread(input_path_images+"/"+f) 
	
	
	out_file_xml = default_out_dir + "/mesures_" + f.split(".")[0] + ".xml"
	file_xml = open(out_file_xml, "w")
	

	file_xml.write("<?xml version=\"1.0\" ?>\n")
	file_xml.write("<SetOfMesureAppuisFlottants>\n")
	file_xml.write("    <MesureAppuiFlottant1Im>\n")
	file_xml.write("        <NameIm>" + f + "</NameIm>\n")

	
	for i in range(len(POINTS_NAME)):
	#for i in range(7,8):
		crop = img_current[LLY[i]-margin:URY[i]+margin, LLX[i]-margin:URX[i]+margin, :]
		crop_us = upsample(crop, factor=frsz)[:,:,0]
		CORREL = phaseCorrelation(crop_us, VIGNETS[i])
				
		dx  = CORREL[0]/frsz-margin - REF_X[i]
		dy  = CORREL[1]/frsz-margin - REF_Y[i]
	
		center = (POINTS_X[i] + dx, POINTS_Y[i] + dy)
		
		print("["+POINTS_NAME[i]+"]", '{:7.3f}'.format(dx), '{:7.3f}'.format(dy), "   ", '{:7.3f}'.format(center[0]), '{:7.3f}'.format(center[1]))

		# -----------------------------------------------------------------
		# Graphical output
		# -----------------------------------------------------------------
		center_vignet = ((URY[i]-LLY[i])/2.0 + dx + margin, (URX[i]-LLX[i])/2.0 + dy + margin)
		crop_us_output = upsample(crop, factor=10, method=cv2.INTER_NEAREST)
		cv2.circle(crop_us_output, (int(10*center_vignet[0]), int(10*center_vignet[1])), 10, (0,0,255), 2)		
		out_file = default_out_dir+"/vignets/"+POINTS_NAME[i]+"/"+f.split('.')[0]+"_"+POINTS_NAME[i]+".png"
		cv2.imwrite(out_file, crop_us_output) 
		# -----------------------------------------------------------------
				
		
		file_xml.write("        <OneMesureAF1I>\n")
		file_xml.write("            <NamePt>" + POINTS_NAME[i] + "</NamePt>\n")
		file_xml.write("            <PtIm>" + str(center[0]) + " " + str(center[1]) + "</PtIm>\n")
		file_xml.write("        </OneMesureAF1I>\n")
		
		
	file_xml.write("    </MesureAppuiFlottant1Im>\n")
	file_xml.write("</SetOfMesureAppuisFlottants>\n")
	file_xml.close()

		
print("----------------------------------------------------------------")



