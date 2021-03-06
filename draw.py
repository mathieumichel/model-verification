import os, numpy, re
from texttable import Texttable
t = Texttable()
t.add_row(["Ratio", "XP (#)", "MAC", "Avg PDR (%)", "Avg latency (ms)", "Avg strobes (#)", "ACKS (%)"])
count=6
from pylab import *

matplotlib.rcParams.update({'font.size': 14})



def regenerateStats():
	ratios=[1,2,4]
	for ratio in ratios:
		i=1
		while i<=count:
			dir1="experiment-phaselock/tests/umons-nullmac"+"-"+str(ratio)+"-xp"+str(i)
			dir2="experiment/tests/sics-nullmac"+"-"+str(ratio)+"-xp"+str(i)
			os.system("python scripts/analyze-log-serial.py "+dir1+"/merged-log.txt | tee "+dir1+"/stats.txt")
			os.system("python scripts/analyze-log-serial.py "+dir2+"/merged-log.txt | tee "+dir2+"/stats.txt")
			dir1="experiment-phaselock/tests/umons-csma"+"-"+str(ratio)+"-xp"+str(i)
			dir2="experiment/tests/sics-csma"+"-"+str(ratio)+"-xp"+str(i)
			os.system("python scripts/analyze-log-serial.py "+dir1+"/merged-log.txt | tee "+dir1+"/stats.txt")
			os.system("python scripts/analyze-log-serial.py "+dir2+"/merged-log.txt | tee "+dir2+"/stats.txt")
			i+=1

def computeStatsTotal(xpname,ratio, module):
	i=1
	pdr=0
	latencies=[]
	pdrs=[]
	strobes=[]
	acks=[]
	loss=[]
	dc1=[]
	dc2=[]
	dc3=[]
	xpcount=0;
	while i<=5:
		if xpname=="umons":
			file="experiment-phaselock/tests/"+xpname+"-"+module+"-"+str(ratio)+"-xp"+str(i)+"/stats.txt"
		else:
			file="experiment/tests/"+xpname+"-"+module+"-"+str(ratio)+"-xp"+str(i)+"/stats.txt"
		for line in open(file, 'r').readlines():
			res1=re.compile('(Mean latency: )(\d*.\d*)( ms)').match(line)
			res2=re.compile('(PRR: )(\d*.\d*)').match(line)
			res3=re.compile('(Strobes: )(\d*.\d*)').match(line)
			res4=re.compile('(Received acks: )(\d*.\d*)').match(line)
			res5=re.compile('(Phases lost: )(\d*)').match(line)
			res6=re.compile('(Duty Cycle Total )(\d*.\d*)').match(line)
			res7=re.compile('(Duty Cycle TX )(\d*.\d*)').match(line)
			res8=re.compile('(Duty Cycle RX )(\d*.\d*)').match(line)
			if res1:
				#if float(res1.group(2)) > 1000:
				#	break
				latencies.append(float(res1.group(2)))
				xpcount+=1
			elif res2:
				pdrs.append(float(res2.group(2)))
			elif res3:
				if str(res3.group(2))!='n':
					strobes.append(float(res3.group(2)))
				else:
					print "plop",file
			elif res4:
				acks.append(float(res4.group(2)))
			elif res5:
				loss.append(int(res5.group(2)))
			elif res6:
				dc1.append(float(res6.group(2)))
			elif res7:
				dc2.append(float(res7.group(2)))
			elif res8:
				dc3.append(float(res8.group(2)))
		i+=1
	return "%.2f" % (numpy.mean(pdrs)*100), "%.2f" % (numpy.max(pdrs)*100), "%.2f" % (numpy.min(pdrs)*100), "%.2f" % (numpy.mean(latencies)), "%.2f" % (numpy.max(latencies)), "%.2f" % (numpy.min(latencies)),numpy.mean(loss),"%.2f" %numpy.mean(dc1),"%.2f" %numpy.mean(dc2),"%.2f" %numpy.mean(dc3)
	#t.add_row([str(ratio), xpname.upper()+" ("+str(xpcount)+")", module, "%.2f" % (numpy.mean(pdrs)*100)+" ( +/- "+"%.2f" % (numpy.std(pdrs)*100)+ ")" , "%.2f" % (numpy.mean(latencies)) +" ( +/- "+"%.2f" % (numpy.std(latencies))+ ")", "%.2f" % (numpy.mean(strobes)) +" ( +/- "+"%.2f" % (numpy.std(strobes))+ ")","%.2f" % (numpy.mean(acks)*100) +" ( +/- "+"%.2f" % (numpy.std(acks)*100)+ ")"])


def drawStatsLatency(module, top):
	fig=plt.figure(figsize=(9,6))
	#fig.suptitle(module+" experiments stats")

	plt.ylabel("Avg Latency (ms)")
	plt.xlabel("Interference level (%)")
	plt.xlim([-1,28])
	#plt.ylim([0,110])

	# ax3=fig.add_subplot(3,1,3)
	# ax3.set_ylabel("Phases dropped (#)")
	# ax3.set_xlabel("Interference levels")
	# ax3.set_xlim([-1,17])

	x=[1,6,11,16,21,26]
	x_offset1=map(lambda x:x-0.5, x)
	x_offset2=map(lambda x:x+0.5, x)
	x_offset3=map(lambda x:x-1.5, x)
	plt.xticks(x)
	plt.gca().xaxis.set_ticklabels([0,7,11,20,33,50])
	pdrs1=[]
	pdrs1M=[]
	pdrs1m=[]

	pdrs2=[]
	pdrs2M=[]
	pdrs2m=[]

	lats1=[]
	lats1M=[]
	lats1m=[]

	lats2=[]
	lats2M=[]
	lats2m=[]
	list=[0,12,8,4,2,1]
	for value in list:
		pdr1,pdr1a,pdr1b,lat1,lat1a,lat1b,loss1,dc1A,dc2A,dc3A=computeStatsTotal("umons",value,module)
		pdr2,pdr2a,pdr2b,lat2,lat2a,lat2b,loss2,dc1B,dc2B,dc3B=computeStatsTotal("sics",value,module)
		pdrs1.append(float(pdr1))
		pdrs1M.append(float(pdr1a))
		pdrs1m.append(float(pdr1b))
		pdrs2.append(float(pdr2))
		pdrs2M.append(float(pdr2a))
		pdrs2m.append(float(pdr2b))
		lats1.append(float(lat1))
		lats1M.append(float(lat1a))
		lats1m.append(float(lat1b))
		lats2.append(float(lat2))
		lats2M.append(float(lat2a))
		lats2m.append(float(lat2b))

	coords=[[0.6,1.4],[5.6,6.4],[10.6,11.4],[15.6,16.4],[21.6,21.4],[26.6,26.4]]
	coords2=[[0.6+0.4,1.4+0.4],[5.6+0.4,6.4+0.4],[10.6+0.4,11.4+0.4],[15.6+0.4,16.4+0.4],[21.6+0.4,21.4+0.4],[26.6+0.4,26.4+0.4]]

	if module=="nullmac":
		lats3=[154,251,290,379,472,524]
	else:
		lats3=[154,251,290,379,472,524]

	rects3=plt.bar(x_offset3,lats3,1,color='black',edgecolor='black',label='ContikiMAC model')

	rects1=plt.bar(x_offset1,lats1,1,color='white',edgecolor='black',label='Soft-ACK ContikiMAC', hatch='*')
	rects2=plt.bar(x_offset2,lats2,1,color='grey',label='Default ContikiMAC')

	# rects3=plt.bar(x_offset3,lats3,0.4,color='red',edgecolor='red',label='Contikimac model')
	# rects1=plt.bar(x_offset1,lats1,0.4,color='blue',edgecolor='blue',label='Adv Contikimac')
	# rects2=plt.bar(x_offset2,lats2,0.4,color='green',edgecolor='green',label='Default Contikimac')

	#rects1=ax3.bar(x_offset1,losses1,0.4,color='blue',edgecolor='blue',label='Adv Contikimac')
	#rects2=ax3.bar(x_offset2,losses2,0.4,color='green',edgecolor='green',label='Default Contikimac')

	# for i in range(4):
	# 	plt.plot(coords[i],[lats1M[i],lats1M[i]],':',color='r',linewidth=2)
	# 	plt.plot(coords[i],[lats1m[i],lats1m[i]],':',color='r',linewidth=2)	
	# 	plt.plot(coords2[i],[lats2M[i],lats2M[i]],':',color='r',linewidth=2)
	# 	plt.plot(coords2[i],[lats2m[i],lats2m[i]],':',color='r',linewidth=2)

	if top==1:
		plt.legend(loc="upper left", shadow=True, fontsize=15)
	else:
		plt.legend(loc="upper left", shadow=True, fontsize=15)
	plt.savefig('%s.pdf' %("stats-latency"+str(module)), format='pdf')

def drawStatsPDR(module,top):
	fig=plt.figure(figsize=(12,8))
	#fig.suptitle(module+" experiments stats")

	plt.ylabel("Avg PDR (%)")
	plt.xlabel("Interference level (%)")
	plt.xlim([-1,40])
	plt.ylim([0,110])

	# ax3=fig.add_subplot(3,1,3)
	# ax3.set_ylabel("Phases dropped (#)")
	# ax3.set_xlabel("Interference levels")
	# ax3.set_xlim([-1,17])

	x=[1,6,11,16,21,26]
	offset_tmp=0.5
	x_offset1=map(lambda x:x-0.5, x)
	x_offset2=map(lambda x:x+0.5, x)
	x_offset3=map(lambda x:x-1.5, x)
	plt.xticks(x)
	plt.gca().xaxis.set_ticklabels([0,7,11,20,33,50])
	pdrs1=[]
	pdrs1M=[]
	pdrs1m=[]

	pdrs2=[]
	pdrs2M=[]
	pdrs2m=[]

	lats1=[]
	lats1M=[]
	lats1m=[]

	lats2=[]
	lats2M=[]
	lats2m=[]
	list=[0,12,8,4,2,1]
	for value in list:
		pdr1,pdr1a,pdr1b,lat1,lat1a,lat1b,loss1,dc1A,dc2A,dc3A=computeStatsTotal("umons",value,module)
		pdr2,pdr2a,pdr2b,lat2,lat2a,lat2b,loss2,dc1B,dc2B,dc3B=computeStatsTotal("sics",value,module)
		pdrs1.append(float(pdr1))
		pdrs1M.append(float(pdr1a))
		pdrs1m.append(float(pdr1b))
		pdrs2.append(float(pdr2))
		pdrs2M.append(float(pdr2a))
		pdrs2m.append(float(pdr2b))
		lats1.append(float(lat1))
		lats1M.append(float(lat1a))
		lats1m.append(float(lat1b))
		lats2.append(float(lat2))
		lats2M.append(float(lat2a))
		lats2m.append(float(lat2b))

	#coords=[[0.6,1.4],[5.6,6.4],[10.6,11.4],[15.6,16.4],[21.6,21.4],[26.6,26.4]]
	#coords2=[[0.6+0.4,1.4+0.4],[5.6+0.4,6.4+0.4],[10.6+0.4,11.4+0.4],[15.6+0.4,16.4+0.4],[21.6+0.4,21.4+0.4],[26.6+0.4,26.4+0.4]]


	if module=="csma":
		pdrs3=[100,99.8,99.5,97.2,86.7,54.2]#pcca=95
		pdrs3b=[99.9,99.6,99.2,96.1,85,52.1]#pcca=90
		pdrs3c=[100,99.9,99.7,97.8,88.1,55.9]#pcca=99
	else:
		pdrs3=[95,80.4,74.4,59.2,39.7,17.7]#pcca=95
		pdrs3b=[90,76.1,70.5,56,38,16.8]#pcca=90
		pdrs3c=[99,83.8,77.5,61.8,41.3,18.5]#pcca=99


	rects3=plt.bar(x_offset3,pdrs3c,1,color='black',edgecolor='black',label='ContikiMAC model\n (pcca=0.99)')
	rects3=plt.bar(x_offset3,pdrs3,1,color='white',edgecolor='black',label='ContikiMAC model\n (pcca=0.95)')
	rects3=plt.bar(x_offset3,pdrs3b,1,color='lightgrey',edgecolor='black',label='ContikiMAC model\n (pcca=0.90)',hatch='//')

	rects1=plt.bar(x_offset1,pdrs1,1,color='white',edgecolor='black',label='Soft-ACK ContikiMAC', hatch='*')
	rects2=plt.bar(x_offset2,pdrs2,1,color='grey',label='Default ContikiMAC')

	#rects1=ax3.bar(x_offset1,losses1,0.4,color='blue',edgecolor='blue',label='Adv Contikimac')
	#rects2=ax3.bar(x_offset2,losses2,0.4,color='green',edgecolor='green',label='Default Contikimac')

	# for i in range(4):
	# 	plt.plot(coords[i],[pdrs1M[i],pdrs1M[i]],':',color='r',linewidth=2)
	# 	plt.plot(coords[i],[pdrs1m[i],pdrs1m[i]],':',color='r',linewidth=2)	
	# 	plt.plot(coords2[i],[pdrs2M[i],pdrs2M[i]],':',color='r',linewidth=2)
	# 	plt.plot(coords2[i],[pdrs2m[i],pdrs2m[i]],':',color='r',linewidth=2)

	if top==1:
		plt.legend(loc="upper right", shadow=True, fontsize=15)
	else:
		plt.legend(loc="upper right", shadow=True, fontsize=15)
	plt.savefig('%s.pdf' %("stats-PDR"+str(module)), format='pdf')

def drawStatsTotal(module):
	fig=plt.figure(figsize=(14,4*2))
	fig.suptitle(module+" experiments stats")
	subplots_adjust(hspace=0)

	ax1=fig.add_subplot(2,1,1)
	ax1.set_ylabel("Avg PDR (%)")
	ax1.set_xlim([-1,17])
	ax1.set_ylim([0,110])

	ax2=fig.add_subplot(2,1,2)
	ax2.set_ylabel("Avg Latency (ms)")
	ax2.set_xlim([-1,17])

	# ax3=fig.add_subplot(3,1,3)
	# ax3.set_ylabel("Phases dropped (#)")
	# ax3.set_xlabel("Interference levels")
	# ax3.set_xlim([-1,17])

	x=[1,6,11,16]
	x_offset1=map(lambda x:x-0.2, x)
	x_offset2=map(lambda x:x+0.2, x)
	plt.setp([ax1,ax2],xticks=x,xticklabels=[0,20,30,50])

	pdrs1=[]
	pdrs1M=[]
	pdrs1m=[]

	pdrs2=[]
	pdrs2M=[]
	pdrs2m=[]

	lats1=[]
	lats1M=[]
	lats1m=[]

	lats2=[]
	lats2M=[]
	lats2m=[]
	

	list=[0,4,2,1]
	for value in list:
		pdr1,pdr1a,pdr1b,lat1,lat1a,lat1b,loss1,dc1A,dc2A,dc3A=computeStatsTotal("umons",value,module)
		pdr2,pdr2a,pdr2b,lat2,lat2a,lat2b,loss2,dc1B,dc2B,dc3B=computeStatsTotal("sics",value,module)
		pdrs1.append(float(pdr1))
		pdrs1M.append(float(pdr1a))
		pdrs1m.append(float(pdr1b))
		pdrs2.append(float(pdr2))
		pdrs2M.append(float(pdr2a))
		pdrs2m.append(float(pdr2b))
		lats1.append(float(lat1))
		lats1M.append(float(lat1a))
		lats1m.append(float(lat1b))
		lats2.append(float(lat2))
		lats2M.append(float(lat2a))
		lats2m.append(float(lat2b))

	rects1=ax1.bar(x_offset1,pdrs1,0.4,color='blue',edgecolor='blue')
	rects2=ax1.bar(x_offset2,pdrs2,0.4,color='green',edgecolor='green')
	coords=[[0.6,1.4],[5.6,6.4],[10.6,11.4],[15.6,16.4]]
	coords2=[[0.6+0.4,1.4+0.4],[5.6+0.4,6.4+0.4],[10.6+0.4,11.4+0.4],[15.6+0.4,16.4+0.4]]

	rects1=ax2.bar(x_offset1,lats1,0.5,color='blue',edgecolor='blue',label='Adv Contikimac')
	rects2=ax2.bar(x_offset2,lats2,0.5,color='green',edgecolor='green',label='Default Contikimac')

	#rects1=ax3.bar(x_offset1,losses1,0.4,color='blue',edgecolor='blue',label='Adv Contikimac')
	#rects2=ax3.bar(x_offset2,losses2,0.4,color='green',edgecolor='green',label='Default Contikimac')

	for i in range(4):
		ax1.plot(coords[i],[pdrs1M[i],pdrs1M[i]],':',color='r',linewidth=2)
		ax1.plot(coords[i],[pdrs1m[i],pdrs1m[i]],':',color='r',linewidth=2)
		ax2.plot(coords[i],[lats1M[i],lats1M[i]],':',color='r',linewidth=2)
		ax2.plot(coords[i],[lats1m[i],lats1m[i]],':',color='r',linewidth=2)
		ax1.plot(coords2[i],[pdrs2M[i],pdrs2M[i]],':',color='r',linewidth=2)
		ax1.plot(coords2[i],[pdrs2m[i],pdrs2m[i]],':',color='r',linewidth=2)	
		ax2.plot(coords2[i],[lats2M[i],lats2M[i]],':',color='r',linewidth=2)
		ax2.plot(coords2[i],[lats2m[i],lats2m[i]],':',color='r',linewidth=2)


	ax2.legend(loc="lower right", shadow=True, fontsize=15)
	plt.savefig('%s.pdf' %("stats-"+str(module)), format='pdf')


def drawLosses():
	fig=plt.figure(figsize=(9,6))
	#fig.suptitle("Number of phaselock losses")
	plt.ylabel("Phase-lock dropped (#)")
	plt.xlabel("Interference level (%)")
	plt.gca().set_ylim([0,60])
	plt.gca().set_xlim([-1,23])
	plt.gca().xaxis.set_ticklabels([7,11,20,33,50])
	x=[1,6,11,16,21]
	plt.xticks(x)
	#plt.gca().xaxis.set_ticklabels([0,12.5,25,50])
	lost1=[]
	lost2=[]
	list=[12,8,4,2,1]
	for value in list:
		pdr1,pdr1a,pdr1b,lat1,lat1a,lat1b,loss1,dc1A,dc2A,dc3A=computeStatsTotal("sics",value,"csma")
		pdr1,pdr1a,pdr1b,lat1,lat1a,lat1b,loss2,dc1B,dc2B,dc3B=computeStatsTotal("sics",value,"nullmac")
		lost1.append(int(loss1))
		lost2.append(int(loss2))

	x_offset1=map(lambda x:x-1.1, x)
	x_offset2=map(lambda x:x+0.1, x)
	#plt.plot(x,lost1,linestyle="-",label="CSMA",linewidth=4)
	#plt.plot(x,lost2,linestyle="--",label="NULLMAC",linewidth=4)

	rects2=plt.bar(x_offset1,lost2,1,color='grey',edgecolor='black',label='NO CSMA')
	rects1=plt.bar(x_offset2,lost1,1,color='white',edgecolor='black',label='CSMA',hatch='/')

	plt.legend(loc='upper right', shadow=True, fontsize='15')
	plt.savefig('%s.pdf' %("countLosses"), format='pdf')

def drawDC():
	fig=plt.figure(figsize=(14,4*2))
	fig.suptitle("Duty Cycle stats")
	subplots_adjust(hspace=0)

	ax1=fig.add_subplot(3,1,1)
	ax1.set_ylabel("Duty Cycle (%)")
	ax1.set_xlim([-1,17])

	ax2=fig.add_subplot(3,1,2)
	ax2.set_ylabel("TX Duty Cycle (%)")
	ax2.set_xlim([-1,17])

	ax3=fig.add_subplot(3,1,3)
	ax3.set_ylabel("RX Duty Cycle (%)")
	ax3.set_xlabel("Interference levels")
	ax3.set_xlim([-1,17])

	x=[1,6,11,16]
	x_offset1=map(lambda x:x-0.2, x)
	x_offset2=map(lambda x:x+0.2, x)

	plt.setp([ax1,ax2,ax3],xticks=x,xticklabels=[0,20,33,50])
	list=[0,4,2,1]
	duty1A=[]
	duty2A=[]
	duty3A=[]
	duty1B=[]
	duty2B=[]
	duty3B=[]
	for value in list:
		pdr1,pdr1a,pdr1b,lat1,lat1a,lat1b,loss1,dc1A,dc2A,dc3A=computeStatsTotal("umons",value,"nullmac")
		pdr1,pdr1a,pdr1b,lat1,lat1a,lat1b,loss2,dc1B,dc2B,dc3B=computeStatsTotal("sics",value,"nullmac")
		duty1A.append(float(dc1A))
		duty2A.append(float(dc2A))
		duty3A.append(float(dc3A))
		duty1B.append(float(dc1B))
		duty2B.append(float(dc2B))
		duty3B.append(float(dc3B))


	print duty1A
	print duty1B

	rects1=ax1.bar(x_offset1,duty1A,0.4,color='blue',edgecolor='blue')
	rects2=ax1.bar(x_offset2,duty1B,0.4,color='green',edgecolor='green')

	rects1=ax2.bar(x_offset1,duty2A,0.4,color='blue',edgecolor='blue')
	rects2=ax2.bar(x_offset2,duty2B,0.4,color='green',edgecolor='green')

	rects1=ax3.bar(x_offset1,duty3A,0.4,color='blue',edgecolor='blue',label='Adv Contikimac')
	rects2=ax3.bar(x_offset2,duty3B,0.4,color='green',edgecolor='green',label='Default Contikimac')

	plt.legend(loc='upper left', shadow=True, fontsize='15')
	plt.savefig('%s.pdf' %("dutyCycle"), format='pdf')


def computeStrobesStats(xpname,ratio,index):
	if "sics" in xpname:
		filename="experiment/tests/"+xpname+"-"+str(ratio)+"-xp"+str(index)+"/merged-log.txt"
	else:
		filename="experiment-phaselock/tests/"+xpname+"-"+str(ratio)+"-xp"+str(index)+"/merged-log.txt"
	Strobes=[]
	for line in open(filename).readlines():
		line_vector = line.strip().split()
		if len(line_vector) < 4:
			continue;
		msg_type = line_vector[1]
		if msg_type == "contikimac:":
			if line_vector[2]=="send":#and line_vector[5]=="ack,":
				number_of_strobes = int(line_vector[3].split('=')[1][:-1])
				Strobes.append(number_of_strobes+1)#+1 is because contikimac doesn't account the last final packets only strobes to wake up
	return Strobes
	
def cdfStrobes(tab1, name1, tab2, name2):
	fig=plt.figure(figsize=(9,6))
	#plt.title("Strobes count CDF")
	plt.xlabel("# strobes")
	plt.ylabel("CDF")
	y=sort(tab1)
	yvals=np.arange(len(y))/float(len(y))
	plt.plot(y,yvals,'-',label=name1,color='green',linestyle="-", linewidth=4 )
	y = sort(tab2)
	yvals=np.arange(len(y))/float(len(y))
	plt.plot(y,yvals,'-',label=name2,color='blue',linestyle="--", linewidth=4 )
	plt.xticks([0,5,10,15,20,25])
	ax=plt.gca()
	ax.set_xlim([0,26])
	plt.plot([5,5],[0,1], ':', color='red', linewidth=3)
	ax.annotate('strobes limit once \n the phase learned!',xy=(5,0),xycoords='data',xytext=(7,0.1),textcoords='data',
	arrowprops=dict(facecolor='red',shrink=0.05, frac=0.2, width=2),size=15, color='red')
	#ax.xaxis.set_ticklabels([0,"4\n Max strobes #\n once the phase learned!",5,10,15,20,25])
	ax.xaxis.get_ticklabels()[1].set_color('r')
	ax.legend(loc='right', shadow=True, fontsize='15')
	plt.savefig('%s.pdf' %("countSrobes-cdf"), format='pdf')

def draw(tab1,name1):
	plt.figure(figsize=(7,5))
	plt.title("Number of strobes per transmission attempt")
	plt.ylabel("Strobes count")
	plt.xlabel("TX attempts")
	tabX=range(len(tab1))
	plt.plot(tabX,tab1,label=name1,linestyle="-",)
	
	ax=plt.gca()
	ax.annotate('A',xy=(80,3),xycoords='data',xytext=(40,10),textcoords='data',
	arrowprops=dict(facecolor='black',width=0.5),size=18, color='black')
	ax.annotate('B',xy=(220,5),xycoords='data',xytext=(230,10),textcoords='data',
	arrowprops=dict(facecolor='black', width=0.5),size=18, color='black')
	ax.annotate('C',xy=(445,13),xycoords='data',xytext=(350,20),textcoords='data',
	arrowprops=dict(facecolor='black',width=0.5),size=18, color='black')
	ax.annotate('',xy=(175,13),xycoords='data',xytext=(350,20),textcoords='data',
	arrowprops=dict(facecolor='black',width=0.5),size=18, color='black')
	plt.savefig('%s.pdf' %("countSrobes-"+name1), format='pdf')


########################################################

matplotlib.rcParams.update({'font.size': 18})
#regenerateStats()
#cdfStrobes(computeStrobesStats("sics-nullmac",4,1),"Default ContikiMAC",computeStrobesStats("umons-nullmac",4,1),"Soft-ACK ContikiMAC")
# #drawStatsTotal("csma")
# #drawStatsTotal("nullmac")
# drawStatsLatency("nullmac",0)
# drawStatsLatency("csma",1)
matplotlib.rcParams.update({'font.size': 19})
drawStatsPDR("nullmac",1)
drawStatsPDR("csma",0)
#drawLosses()
#draw(computeStrobesStats("sics-nullmac",4,1),"sics-nullmac-4-xp1")
#drawDC()
########################################################

