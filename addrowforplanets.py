import csv

f = open('data.csv', 'rb')
res = open('data1.csv', 'wb')
csvread = csv.reader(f)
csvwrite = csv.writer(res)

atLine = 0
for line in csvread:
	atLine += 1
	print 'at line:',atLine,line
	csvwrite.writerow(line)
	if atLine == 1:
		continue
	if int(line[1])==1:
		n = int(line[10])
		for i in xrange(n):
			csvwrite.writerow( (chr(ord('b')+i), 0) )
f.close()
res.close()
