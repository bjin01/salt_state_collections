#!/bin/bash
SIDADM=$1
INSTANCENR=$2
SID=$3
APPNAME=$4
su - ${SIDADM} -c "sapcontrol -nr ${INSTANCENR} -function StartService $SID"
sleep 2

echo "instance-id: $INSTANCENR sidadm is $SIDADM"
su - ${SIDADM} -c "sapcontrol -nr ${INSTANCENR} -function StartSystem ALL"
echo "Wait 2 seconds for starting..."
sleep 2
i=0

while [ $i -lt 30 ]
do
  echo " "
  echo "We are starting SAP ${APPNAME}..."
  su - ${SIDADM} -c "sapcontrol -nr ${INSTANCENR} -function GetProcessList | grep -e GRAY -e YELLOW"
if [ $? -eq 1 ]
  then
          echo "SAP ${APPNAME} is started!"
          su - ${SIDADM} -c "sapcontrol -nr ${INSTANCENR} -function GetProcessList"
          exit 0
fi

echo "Looping to start SAP ${APPNAME} $i"
su - ${SIDADM} -c "sapcontrol -nr ${INSTANCENR} -function GetProcessList >/dev/null 2>&1"
sleep 4
i=$[$i+1]
done
echo "SAP ${APPNAME} not all is started!"