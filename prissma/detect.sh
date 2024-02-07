#!/bin/bash


# -------------------------------------------------------------------------------------------------
# PARAMETRES DU SCRIPT
# -------------------------------------------------------------------------------------------------
target_specif=IGNDroneSym_Nbb10_Freq2_Hamm3_Run2_3_FullSpecif.xml          # Spécifications cibles
MMVII_path=/home/YMeneroux/Bureau/KitYann/Prog/micmac/MMVII/bin/./MMVII    # Chemin absolu MMVII
# -------------------------------------------------------------------------------------------------


DIRECTORY_CAMS=("A124" "A125" "A126" "B130" "C131" "C132" "C133" "D136" "D138" "D149")


FILES="*.jpg"


# Détection des cibles
for cam in "${DIRECTORY_CAMS[@]}"
do
	cd $cam
	
	rm -rf Out
	rm -rf RectifTargets
	mkdir Out
	
	echo "------------------------------"
	echo "Processing camera #"$cam
	echo "------------------------------"
	
	
	for f in $FILES
	do
		echo $f
		convert $f -region 5320x1550+0+0 -blur 101x101 $f
		$MMVII_path CodedTargetExtract $f ../$target_specif DMD=20 Debug=1023 Tolerance=0.05 LinedUpPx=1.5 MaxEcc=9 Binarity=50 Xml=Out/mesures.xml;
		#$MMVII_path CodedTargetExtract $f ../$target_specif DMD=20 Debug=1023 Tolerance=0.05 LinedUpPx=1.5 MaxEcc=3 Vertical=1 Burnt=0.15 Xml=Out/mesures.xml;
		mv VisuCodeTarget.tif Out/VisuCodeTarget${f:0:-4}.tif
		convert Out/VisuCodeTarget${f:0:-4}.tif Out/VisuCodeTarget${f:0:-4}.jpg
		rm Out/VisuCodeTarget${f:0:-4}.tif
	done	
	
	# Fermeture balises fichier de mesures 2D
	sed -i '1s/^/<SetOfMesureAppuisFlottants>\n/' Out/mesures.xml
	sed -i '1s/^/<?xml version="1.0" ?>\n/' Out/mesures.xml
	echo '</SetOfMesureAppuisFlottants>' >> Out/mesures.xml
	
	# Nettoyage dossier
	rm -r MMVII-Tmp-Dir-Glob
	rm -r Tmp-MM-Dir
	rm TestDCT_SYMINIT_SimulTarget_test.tif
	rm MMVII-LogFile.txt
	
	cd ../
done

	

