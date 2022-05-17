#!/bin/bash
SIDADM=$1
INSTANCENR=$2
SID=$3
APPNAME=$4

su - ${SIDADM} -c "sapcontrol -nr ${INSTANCENR} -function StopSystem ALL"
sleep 2
i=0

while [ $i -lt 45 ]
do
  echo " "
  echo "We are stopping SAP ${APPNAME}..."
  su - ${SIDADM} -c "sapcontrol -nr $INSTANCENR -function GetProcessList | grep -e GREEN -e YELLOW"
if [ $? -eq 1 ]
  then
          echo "SAP ${APPNAME} is fully stopped."
          sleep 2
          su - ${SIDADM} -c "sapcontrol -nr $INSTANCENR -function GetProcessList"
          sleep 2
          su - ${SIDADM} -c "sapcontrol -nr ${INSTANCENR} -function StopService $SID"
          sleep 2
          su - ${SIDADM} -c "cleanipc $INSTANCENR remove"
          exit 0
fi

echo "Looping to check SAP ${APPNAME} stopping state $i"
 su - ${SIDADM} -c "sapcontrol -nr $INSTANCENR -function GetProcessList >/dev/null 2>&1"
sleep 4
i=$[$i+1]
done
echo "SAP ${APPNAME} could not be stopped fully!"