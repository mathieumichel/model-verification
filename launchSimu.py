import os, numpy, re
from texttable import Texttable
t = Texttable(max_width=140)
t.add_row(["TXprob", "XP(#)", "MAC", "AvgPDR(%)", "AvgLat(ms)", "AvgStrobes(#)", "ACKS(%)", "Losses", "DC(%)"])
count=5
from pylab import *
ratio=[12,8,4,2,1,0]
tx=[90,85,76.89,54,29.5,100]
probs=dict(zip(ratio,tx))

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
	ratios=[1,2,4]
	for ratio in ratios:
		for mod in ["csma","nullmac"]:
			i=1
			while i<=count:
				dir1="experiment-phaselock/tests/umons-"+mod+"-"+str(ratio)+"-xp"+str(i)
				dir2="experiment/tests/sics-"+mod+"-"+str(ratio)+"-xp"+str(i)
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
	dc=[]
	xpcount=0;
	while i<=count:
		if module=="nullrdc":
			if ratio==0:
				ratio==1
			dir1="/home/macfly/Desktop/tests-nullrdc/"+xpname+"-"+"nullmac"+"-"+str(ratio)+"-xp"+str(i)
			file=dir1+"/stats.txt"
			#os.system("python scripts/analyze-log-serial.py "+dir1+"/merged-log.txt | tee "+dir1+"/stats.txt")
		elif xpname=="umons":
			#dir1="/home/macfly/Desktop/tests-nocca/"+xpname+"-"+module+"-"+str(ratio)+"-xp"+str(i)
			dir1="experiment-phaselock/tests/"+xpname+"-"+module+"-"+str(ratio)+"-xp"+str(i)
			file=dir1+"/stats.txt"
			#os.system("python scripts/analyze-log-serial.py "+dir1+"/merged-log.txt | tee "+dir1+"/stats.txt")
		else:
			dir1="experiment/tests/"+xpname+"-"+module+"-"+str(ratio)+"-xp"+str(i)
			file=dir1+"/stats.txt"
			#os.system("python scripts/analyze-log-serial.py "+dir1+"/merged-log.txt | tee "+dir1+"/stats.txt")
		if not os.path.isfile(file):
			i+=1
			continue
		for line in open(file, 'r').readlines():
			res1=re.compile('(Mean latency: )(\d*.\d*)( ms)').match(line)
			res2=re.compile('(PRR: )(\d*.\d*)').match(line)
			res3=re.compile('(Strobes: )(\d*.\d*)').match(line)
			res4=re.compile('(Received acks: )(\d*.\d*)').match(line)
			res5=re.compile('(Phases lost: )(\d*)').match(line)
			res6=re.compile('(Duty Cycle Total )(\d*.\d*)').match(line)
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
				dc.append(float(res6.group(2)))
		i+=1
	t.add_row([str(probs[ratio]), xpname.upper()+"("+str(xpcount)+")", module, "%.2f" % (numpy.mean(pdrs)*100)+"(+/-"+"%.2f" % (numpy.std(pdrs)*100)+ ")" ,
	 "%.2f" % (numpy.mean(latencies)) +"(+/-"+"%.2f" % (numpy.std(latencies))+ ")",
	  "%.2f" % (numpy.mean(strobes)) +"(+/-"+"%.2f" % (numpy.std(strobes))+ ")",
	  "%.2f" % (numpy.mean(acks)*100) +"(+/-"+"%.2f" % (numpy.std(acks)*100)+ ")",
	   numpy.mean(loss),
	   "%.2f" % numpy.mean(dc)])




########################################################
#list=[1,2,4]
#for value in list:
#	start(value)
########################################################
list=[0,1,2,4,8,12]
for value in list:
	#computeStatsTotal("sics",value,"nullrdc")
	computeStatsTotal("umons",value,"csma")
 	computeStatsTotal("umons",value,"nullmac")
 	computeStatsTotal("sics",value,"csma")
 	computeStatsTotal("sics",value,"nullmac")
print t.draw()

