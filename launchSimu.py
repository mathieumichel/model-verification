import os, numpy, re
from texttable import Texttable
t = Texttable()
t.add_row(["Ratio", "XP (#)", "MAC", "Avg PDR (%)", "Avg latency (ms)", "Avg strobes (#)", "ACKS (%)"])
count=15
from pylab import *


def changeMacLayer(module):
	os.system("sed \"s/#define NETSTACK_CONF_MAC.*/\#define NETSTACK_CONF_MAC "+module+"_driver/\" project-conf.h > temp.h")
	os.system("mv temp.h project-conf.h")
	os.system("chmod 777 project-conf.h")

#launch all umons xp than all sics xp
def start(ratio):
	#change the ratio for interferer
	os.chdir("experiment")
	os.system("sed \"s/#define INTERFERER_OFF_TIME INTERFERER_ON_TIME * .*/\#define INTERFERER_OFF_TIME INTERFERER_ON_TIME * "+str(ratio)+"/\" project-conf.h > temp.h")
	os.system("mv temp.h project-conf.h")
	os.system("chmod 777 project-conf.h")
	os.system("make interferer.upload TARGET=z1 MOTE=3")
	os.chdir("..")

	#umons code
	
	os.chdir("experiment-phaselock")
	
	i=0
	module="nullmac"
	changeMacLayer(module)
	os.system("make net-test.upload TARGET=z1 MOTE=1")
	os.system("make net-test.upload TARGET=z1 MOTE=2")
	while i<count:
		os.system("./umons-experiment.sh tests/umons-"+module+"-"+str(ratio)+"-xp"+str(i+1))
		i+=1
	i=0
	module="csma"
	changeMacLayer(module)
	os.system("make net-test.upload TARGET=z1 MOTE=1")
	os.system("make net-test.upload TARGET=z1 MOTE=2")
	while i<count:
		os.system("./umons-experiment.sh tests/umons-"+module+"-"+str(ratio)+"-xp"+str(i+1))
		i+=1
		
	os.chdir("..")
	
	#sics code
	os.chdir("experiment")
	i=0
	module="nullmac"
	changeMacLayer(module)
	os.system("make net-test.upload TARGET=z1 MOTE=1")
	os.system("make net-test.upload TARGET=z1 MOTE=2")
	os.chdir("../experiment-phaselock")
	while i<count:
		os.system("./umons-experiment.sh tests/sics-"+module+"-"+str(ratio)+"-xp"+str(i+1))
		i+=1
	i=0
	module="csma"
	os.chdir("../experiment")
	changeMacLayer(module)
	os.system("make net-test.upload TARGET=z1 MOTE=1")
	os.system("make net-test.upload TARGET=z1 MOTE=2")
	os.chdir("../experiment-phaselock")
	while i<count:
		os.system("./umons-experiment.sh tests/sics-"+module+"-"+str(ratio)+"-xp"+str(i+1))
		i+=1
	i=0
	os.chdir("..")


#launch umons and sics xps in an alternate way
def startB(ratio, mode):
	
	#change the ratio for interferer
	os.chdir("experiment")
	os.system("sed \"s/#define INTERFERER_OFF_TIME INTERFERER_ON_TIME * .*/\#define INTERFERER_OFF_TIME INTERFERER_ON_TIME * "+str(ratio)+"/\" project-conf.h > temp.h")
	os.system("mv temp.h project-conf.h")
	os.system("chmod 777 project-conf.h")
	os.system("make interferer.upload TARGET=z1 MOTE=3")
	os.chdir("..")
	#os.system("rm -rf experiment-phaselock/tests/umons-"+str(ratio)+"-xp*")
	#os.system("rm -rf experiment-phaselock/tests/sics-"+str(ratio)+"-xp*")
	i=1
	
	if mode==0:
		module="nullmac"
	elif mode==1:
		module="csma"
	elif mode==2:
		module="nullmac"
		
	os.chdir("experiment")
	os.system("sed \"s/#define NETSTACK_CONF_MAC.*/\#define NETSTACK_CONF_MAC "+module+"_driver/\" project-conf.h > temp.h")
	os.system("mv temp.h project-conf.h")
	os.system("chmod 777 project-conf.h")
	os.chdir("../experiment-phaselock")
	os.system("sed \"s/#define NETSTACK_CONF_MAC.*/\#define NETSTACK_CONF_MAC "+module+"_driver/\" project-conf.h > temp.h")
	os.system("mv temp.h project-conf.h")
	os.system("chmod 777 project-conf.h")
	os.chdir("..")
	
	while i<=count:
		#umons code
		os.chdir("experiment-phaselock")
		os.system("make net-test.upload TARGET=z1 MOTE=1")
		os.system("make net-test.upload TARGET=z1 MOTE=2")
		os.system("./umons-experiment.sh tests/umons-"+module+"-"+str(ratio)+"-xp"+str(i))
		os.chdir("..")
		#sics code
		os.chdir("experiment")
		os.system("make net-test.upload TARGET=z1 MOTE=1")
		os.system("make net-test.upload TARGET=z1 MOTE=2")
		os.chdir("../experiment-phaselock")
		os.system("./umons-experiment.sh tests/sics-"+module+"-"+str(ratio)+"-xp"+str(i))
		os.chdir("..")
		i+=1
		if(i>count and mode==2): #we test now with csma_driver
			i=1
			module="csma"
			os.chdir("experiment")
			os.system("sed \"s/#define NETSTACK_CONF_MAC.*/\#define NETSTACK_CONF_MAC "+module+"_driver/\" project-conf.h > temp.h")
			os.system("mv temp.h project-conf.h")
			os.system("chmod 777 project-conf.h")
			os.chdir("../experiment-phaselock")
			os.system("sed \"s/#define NETSTACK_CONF_MAC.*/\#define NETSTACK_CONF_MAC "+module+"_driver/\" project-conf.h > temp.h")
			os.system("mv temp.h project-conf.h")
			os.system("chmod 777 project-conf.h")
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
		file="experiment-phaselock/tests/"+xpname+"-"+module+"-"+str(ratio)+"-xp"+str(i)+"/stats.txt"
		for line in open(file, 'r').readlines():
			res1=re.compile('(Mean latency: )(\d*.\d*)( ms)').match(line)
			res2=re.compile('(PRR: )(\d*.\d*)').match(line)
			res3=re.compile('(Strobes: )(\d*.\d*)').match(line)
			res4=re.compile('(Received acks: )(\d*.\d*)').match(line)
			if res1:
				if float(res1.group(2)) > 1000:
					break
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
	filename="experiment-phaselock/tests/"+xpname+"-"+str(ratio)+"-xp"+str(index)+"/merged-log.txt"
	Strobes=[]
	for line in open(filename).readlines():
		line_vector = line.strip().split()
		if len(line_vector) < 4:
			continue;
		msg_type = line_vector[1]
		if msg_type == "contikimac:":
			if line_vector[2]=="send":# and line_vector[5]=="ack,":
				number_of_strobes = int(line_vector[3].split('=')[1][:-1])
				Strobes.append(number_of_strobes)
	return Strobes

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

def baseline(ratio):
	#change the ratio for interferer
	os.chdir("experiment")
	os.system("sed \"s/#define INTERFERER_OFF_TIME INTERFERER_ON_TIME * .*/\#define INTERFERER_OFF_TIME INTERFERER_ON_TIME * "+str(ratio)+"/\" project-conf.h > temp.h")
	os.system("mv temp.h project-conf.h")
	os.system("chmod 777 project-conf.h")
	os.system("make interferer.upload TARGET=z1 MOTE=3")
	os.chdir("..")

	
	#sics code
	i=0
	os.chdir("experiment")
	os.system("make net-test.upload TARGET=z1 MOTE=1")
	os.system("make net-test.upload TARGET=z1 MOTE=2")
	os.chdir("../experiment-phaselock")
	while i<10:
		os.system("./umons-experiment.sh tests/baseline-sics-"+str(ratio)+"-xp"+str(i+1))
		i+=1
	os.chdir("..")

########################################################
#for ratio in range(10):
	#computeStatsTotal("umons",ratio+1)
	#computeStatsTotal("sics",ratio+1)
########################################################
#list=[1,2,9]
#for value in list:
#	start(value)
########################################################
list=[1,2,9]
for value in list:
	computeStatsTotal("umons",value,"csma")
	computeStatsTotal("umons",value,"nullmac")
	computeStatsTotal("sics",value,"csma")
	computeStatsTotal("sics",value,"nullmac")
print t.draw()
########################################################
#regenerateStats()
########################################################
#draw(computeStrobesStats("sics",1,2),"sics",computeStrobesStats("sics",1,2),"sics")
########################################################
#list=[1,2,9]
#for value in list:
	#baseline(value)
