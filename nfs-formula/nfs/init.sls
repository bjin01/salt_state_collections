{% from "nfs/map.jinja" import mynfs with context %}
{% if salt['grains.get']('fqdn') in salt['pillar.get']('nfs') %}  
{% for h, i in mynfs.items() %} 
nfs_{{ h }}:
  mount.mounted:
    - name: {{ h }}
    - device: {{ i }}
    - fstype: {{ salt['pillar.get']('nfssettings:fstype', 'nfs') }}
    - opts: {{ salt['pillar.get']('nfssettings:mntoptions') }}
    - mkmnt: {{ salt['pillar.get']('nfssettings:create_mount', True) }}
    - persist: {{ salt['pillar.get']('nfssettings:fstab', True) }} 
{% endfor %}
{% endif %}
