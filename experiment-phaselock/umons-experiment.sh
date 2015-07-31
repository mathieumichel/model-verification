#!/bin/bash

FILES=(setup.txt merged-log.txt sender.txt receiver.txt \
	interferer.txt rssi-scanner.txt)

#rm -rf ${FILES[*]}

INTERFERER_PORT=3
#SCANNER_PORT=13
RECEIVER_PORT=2
SENDER_PORT=1


if [ $# -eq 0 ]
	then
	DIR=`date +"experiment_%F_%T"`
else
	DIR=$1
fi

WAIT_TIME=10
MEASUREMENT_TIME=180

echo "Resetting the testbed..."
make z1-reset TARGET=z1
make z1-reset TARGET=z1
make z1-reset TARGET=z1

echo "Starting the RSSI scanner and the interferer"
echo "Running for" $WAIT_TIME "seconds..."

make login MOTE=$INTERFERER_PORT TARGET=z1 |./timestamp > interferer.txt &
#make login CMOTES=$SCANNER_PORT > rssi-scanner.txt &

sleep $WAIT_TIME
echo "Starting the sender and the reader"

make z1-reset TARGET=z1
make z1-reset TARGET=z1
make z1-reset TARGET=z1

make login MOTE=$SENDER_PORT TARGET=z1 |./timestamp > sender.txt &
make login MOTE=$RECEIVER_PORT TARGET=z1 |./timestamp > receiver.txt &

echo "Measuring for" $MEASUREMENT_TIME "seconds..."
sleep $MEASUREMENT_TIME

echo "Terminating the experiment..."
skill -c make TARGET=z1

sleep 1
echo "Moving the files into the directory" $DIR
cat sender.txt receiver.txt | sort -n > merged-log.txt

echo "Experimental setup: " > setup.txt
echo "WAIT_TIME = " $WAIT_TIME >> setup.txt
echo "MEASUREMENT_TIME = " $MEASUREMENT_TIME >> setup.txt
echo "Project Configuration Header:" >> setup.txt
cat project-conf.h >> setup.txt

mkdir $DIR && mv ${FILES[*]} $DIR
cp net-test.c $DIR
../scripts/analyze-log-serial.py $DIR/merged-log.txt | tee $DIR/stats.txt

