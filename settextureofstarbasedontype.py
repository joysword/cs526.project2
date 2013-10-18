import csv

f = open('data2.csv', 'rU')
res = open('data3.csv', 'wb')
csvread = csv.reader(f)
csvwrite = csv.writer(res)

atLine = 0
for line in csvread:
	atLine += 1
	if atLine==1:
		continue
	print 'at line:',atLine
	if int(line[1])==1:
		if cmp(line[8],'O')==0:
			line[3]='textures/o.png'
		elif cmp(line[8],'B')==0:
			line[3]='textures/b.png'
		elif cmp(line[8],'A')==0:
			line[3]='textures/a.jpg'
		elif cmp(line[8],'F')==0:
			line[3]='textures/f.png'
		elif cmp(line[8],'G')==0:
			line[3]='textures/g.png'
		elif cmp(line[8],'K')==0:
			line[3]='textures/k.png'
		elif cmp(line[8],'M')==0:
			line[3]='textures/m.png'

	csvwrite.writerow(line)
f.close()
res.close()
