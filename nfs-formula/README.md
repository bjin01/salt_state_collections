# nfs formula 
This formula is used to create SAP application server and HANA DB nfs shares.
The desired nfs mount options, mount points and nfs servers should be edited in the pillar file in /srv/pillar/nfsmounts/init.sls

## Start to use it:
copy nfs directory to /srv/salt
copy nfsmounts under /srv/pillar

Don't forget to add the pillar nfsmounts to /srv/pillar/top.sls

Modify the /srv/pillar/nfsmounts/init.sls and add your servers, type, sid

To test it:
```salt "*" state.apply nfs test=true ```

To deploy it:
```salt "*" state.apply nfs```
 

