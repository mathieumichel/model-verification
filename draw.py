import os, numpy, re
from texttable import Texttable
t = Texttable()
t.add_row(["Ratio", "XP (#)", "MAC", "Avg PDR (%)", "Avg latency (ms)", "Avg strobes (#)", "ACKS (%)"])
count=5
from pylab import *

matplotlib.rcParams.update({'font.size': 14})


def changeMacLayer(module):
	os.system("sed \"s/#define NETSTACK_CONF_MAC.*/\#define NETSTACK_CONF_MAC "+module+"_driver/\" project-conf.h > temp.h")
	os.system("mv temp.h project-conf.h")
	os.system("chmod 777 project-conf.h")

def changeRatio(ratio):
	os.chdir("interferer")
	os.system("sed \"s/#define INTERFERER_OFF_TIME INTERFERER_ON_TIME * .*/\#define INTERFERER_OFF_TIME INTERFERER_ON_TIME * "+str(ratio)+"/\" project-conf.h > temp.h")
	os.system("mv temp.h project-conf.h")
	os.system("chmod 777 project-conf.h")
	os.system("make interferer.upload TARGET=z1 MOTE=3")
	os.chdir("..")
	
def launchTest(test,ratio,module):
	changeMacLayer(module)
	os.system("make net-test.upload TARGET=z1 MOTE=1")
	os.system("make net-test.upload TARGET=z1 MOTE=2")
	i=0
	while i<count:
		os.system("./umons-experiment.sh tests/"+str(test)+"-"+str(module)+"-"+str(ratio)+"-xp"+str(i+1))
		i+=1


#launch all umons xp than all sics xp
def start(ratio):
	changeRatio(ratio)
	
	#umons code
	os.chdir("experiment-phaselock")
	launchTest("umons",ratio,"nullmac")
	launchTest("umons",ratio,"csma")
	os.chdir("..")
	
	#sics code
	os.chdir("experiment")
	launchTest("sics",ratio,"nullmac")
	launchTest("sics",ratio,"csma")
	os.chdir("..")

def regenerateStats():
	ratios=[1,2,4,9]
	for ratio in ratios:
		i=1
		while i<=count:
			dir1="experiment-phaselock/tests/umons"+"-"+str(ratio)+"-xp"+str(i)
			dir2="experiment-phaselock/tests/sics"+"-"+str(ratio)+"-xp"+str(i)
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
	xpcount=0;
	while i<=count:
		if xpname=="umons":
			file="experiment-phaselock/tests/"+xpname+"-"+module+"-"+str(ratio)+"-xp"+str(i)+"/stats.txt"
		else:
			file="experiment/tests/"+xpname+"-"+module+"-"+str(ratio)+"-xp"+str(i)+"/stats.txt"
		for line in open(file, 'r').readlines():
			res1=re.compile('(Mean latency: )(\d*.\d*)( ms)').match(line)
			res2=re.compile('(PRR: )(\d*.\d*)').match(line)
			res3=re.compile('(Strobes: )(\d*.\d*)').match(line)
			res4=re.compile('(Received acks: )(\d*.\d*)').match(line)
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
		i+=1
	t.add_row([str(ratio), xpname.upper()+" ("+str(xpcount)+")", module, "%.2f" % (numpy.mean(pdrs)*100)+" ( +/- "+"%.2f" % (numpy.std(pdrs)*100)+ ")" , "%.2f" % (numpy.mean(latencies)) +" ( +/- "+"%.2f" % (numpy.std(latencies))+ ")", "%.2f" % (numpy.mean(strobes)) +" ( +/- "+"%.2f" % (numpy.std(strobes))+ ")","%.2f" % (numpy.mean(acks)*100) +" ( +/- "+"%.2f" % (numpy.std(acks)*100)+ ")"])

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
				Strobes.append(number_of_strobes)
	return Strobes
	
def cdfStrobes(tab1, name1, tab2, name2):
	fig=plt.figure(figsize=(8,5))
	plt.title("Strobes count CDF")
	plt.xlabel("# strobes")
	plt.ylabel("TX attempts")
	y=sort(tab1)
	yvals=np.arange(len(y))/float(len(y))
	plt.plot(y,yvals,'-',label=name1,color='green',linestyle="-", linewidth=1 )
	y = sort(tab2)
	yvals=np.arange(len(y))/float(len(y))
	plt.plot(y,yvals,'-',label=name2,color='blue',linestyle="--", linewidth=1 )
	plt.xticks([0,4,5,10,15,20,25])
	ax=plt.gca()
	ax.set_xlim([0,26])
	plt.plot([4,4],[0,1], ':', color='red', linewidth=1)
	ax.annotate('strobes limit once the phase learned!',xy=(4,0),xycoords='data',xytext=(6,0.1),textcoords='data',
	arrowprops=dict(facecolor='red',shrink=0.05, frac=0.2, width=2),size=8, color='red')
	#ax.xaxis.set_ticklabels([0,"4\n Max strobes #\n once the phase learned!",5,10,15,20,25])
	ax.xaxis.get_ticklabels()[1].set_color('r')
	plt.savefig('%s.pdf' %("countSrobes-cdf"), format='pdf')

def draw(tab1,name1,tab2,name2):
	plt.figure(figsize=(7,5))
	plt.title("Evolution number of Strobes")
	plt.ylabel("# strobes")
	plt.xlabel("TX attempts")
	tabX=range(len(tab1))
	plt.plot(tabX,tab1,label=name1,linestyle="-",)
	tabX=range(len(tab2))
	plt.plot(tabX,tab2,label=name2,linestyle="--",)
	plt.savefig('%s.pdf' %("countSrobes-all"), format='pdf')


########################################################
cdfStrobes(computeStrobesStats("sics-nullmac",2,1),"sics",computeStrobesStats("umons-nullmac",2,1),"umons")
########################################################

