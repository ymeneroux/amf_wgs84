DIRECTORY_CAMS=("A126" "A124" "A125" "B130" "C131" "C132" "C133" "D136" "D138" "D149")


for cam in "${DIRECTORY_CAMS[@]}"
do
	cd $cam
	rm -rf Visu
	mkdir Visu
	cp Out/*.jpg Visu/
	cp ../rename.py Visu/
	cd Visu
	/usr/bin/python3 rename.py
	rm rename.py
	ffmpeg -framerate 8 -pattern_type glob -i "*.jpg" out.mp4
	rm *.jpg
	cd ../../
done
