import os

for f in os.listdir("images/"):
	if (f == "rename.py"):
		continue
	name = f.split('.')[0]
	items = name.split('_')
	items2 = items[1].split('-')
	out_name = items[0]+"_"+items2[-5]+"-"+items2[-4]+"-"+items2[-3]+"-"+items2[-2]+"-"+'{:04d}'.format(int(items2[-1]))+".jpg"
	print(f, out_name)
	os.rename("images/"+f, "images/"+out_name)
