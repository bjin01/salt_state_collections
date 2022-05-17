{% set hostfqdn = salt['grains.get']('fqdn') %}
{% set sid = salt['pillar.get']('saphana:' + hostfqdn + ':sid') %}
{% set instid = salt['pillar.get']('saphana:' + hostfqdn + ':instance') %}
{% set clusterip = salt['pillar.get']('saphana:' + hostfqdn + ':clusterip') %}

my_hana_checkip_{{ hostfqdn }}:
  cmd.run:
    - name: ip a | grep {{ clusterip }}

my_hana_mount_check_{{ hostfqdn }}_hanalog:
  cmd.run:
    - name: df -hT |grep "/hana/log"

my_hana_mount_check_{{ hostfqdn }}_hanashared:
  cmd.run:
    - name: df -hT |grep "/hana/shared"

my_hana_mount_check_{{ hostfqdn }}_hanadata:
  cmd.run:
    - name: df -hT |grep "/hana/data"

my_hana_mount_check_{{ hostfqdn }}_usrsap:
  cmd.run:
    - name: df -hT |grep "/usr/sap"

my_hana_{{ hostfqdn }}_start:
  cmd.run:
    - name: /hana/shared/{{ sid|upper }}/HDB{{ instid }}/HDB start
    - runas: {{ sid }}adm
    - output_logleveldebug: True
    - require:
      - cmd: my_hana_checkip_{{ hostfqdn }}
      - cmd: my_hana_mount_check_{{ hostfqdn }}_hanalog
      - cmd: my_hana_mount_check_{{ hostfqdn }}_hanadata
      - cmd: my_hana_mount_check_{{ hostfqdn }}_hanashared
      - cmd: my_hana_mount_check_{{ hostfqdn }}_usrsap

my_hana_{{ hostfqdn }}_onfail_start:
  event.send:
    - name: saphana/failed/tostart
    - data:
      status: "Uups HANA start failed. Alarm."
    - onfail:
      - cmd: my_hana_{{ hostfqdn }}_start