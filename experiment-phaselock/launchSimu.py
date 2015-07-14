import os

define start():
	os.system("cd experiment-phaselock")
	os.system("./umons-experiment.sh")
	

start()
