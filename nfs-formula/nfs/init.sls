{% from "nfs/map.jinja" import mynfs with context %}
{% if salt['grains.get']('fqdn') in salt['pillar.get']('nfs') %}  
{% for h, i in mynfs.items() %} 
nfs_{{ h }}:
  mount.mounted:
    - name: {{ h }}
    - device: {{ i }}
    - fstype: nfs
    - opts: "rw,vers=4,minorversion=1,hard,timeo=600,rsize=1048576,wsize=1048576,bg,noatime,lock"
    - mkmnt: True
    - persist: True
{% endfor %}
{% endif %}




