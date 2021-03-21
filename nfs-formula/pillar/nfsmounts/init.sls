nfs:
  rancher-1.bo2go.home:
    type: test 
    sid: abc
  rancher-2.bo2go.home:
    type: test
    sid: xyz

nfssettings:
  fstype: nfs
  create_mount: True
  fstab: True
  mntoptions: "rw,vers=4,minorversion=1,hard,timeo=600,rsize=1048576,wsize=1048576,bg,noatime,lock"

nfsservers:
  server1: testnfserver1
  server2: testnfsserver2
  server3: sapclient01

