import os

for f in os.listdir("."):
	if (f == "rename.py"):
		continue
	name = f.split('.')[0]
	items = name.split('_')
	items2 = items[1].split('-')
	out_name = "IGN2_"+'{:04d}'.format(int(items2[-1]))+".jpg"
	print(f, out_name)
	os.rename(f, out_name)
