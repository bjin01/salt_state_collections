{% if salt['grains.get']('fqdn') in salt['pillar.get']('nfs') %}  
{% from "nfs/map.jinja" import mynfs with context %}
{% set hostfqdn = salt['grains.get']('fqdn') %}
{% set sid = salt['pillar.get']('nfs:' + hostfqdn + ':sid') %}
fstab-config-block-base:
  file.blockreplace:
    - name: /etc/fstab
    - marker_start: "# START salt managed comment -DO-NOT-EDIT-"
    - marker_end: "# END salt comment --"
    - content: '#'
    - append_if_not_found: True
    - show_changes: True

hosts-config-block-accumulated1:
  file.accumulated:
    - filename: /etc/fstab
    - name: my-accumulator1
    - text: |
         #
         ## Mountpoints {{ sid }}
         #
    - require_in:
      - file: fstab-config-block-base

{% for h, i in mynfs.items() %} 
{% if "error" in i %}
failure_nofound_{{ h }}:
  test.fail_without_changes:
    - name: "No matching nfs ip found in  pillar for this {{ grains.fqdn }} {{ h }} {{ i }} host."
    - failhard: True
{% else %}
nfs_{{ h }}:
  mount.mounted:
    - name: {{ h }}
    - device: {{ i }}
    - fstype: {{ salt['pillar.get']('nfssettings:fstype', 'nfs') }}
    - opts: {{ salt['pillar.get']('nfssettings:mntoptions') }}
    - mkmnt: {{ salt['pillar.get']('nfssettings:create_mount', True) }}
    - persist: {{ salt['pillar.get']('nfssettings:fstab', True) }} 
cmdrun_{{ h }}:
  cmd.run:
    - name: echo '{{ i }} {{ h }}'
{% endif %}
{% endfor %}
{% else %}
failure:
  test.fail_without_changes:
    - name: "No nfs pillar for this {{ grains.fqdn }} defined."
    - failhard: True
{% endif %}
