{% set ports = ['01', '03'] %}
{% set hostfqdn = salt['grains.get']('fqdn') %}
{% set sid = salt['pillar.get']('saphana:' + hostfqdn + ':sid') %}
{% set instid = salt['pillar.get']('saphana:' + hostfqdn + ':instance') %}

my_hana_{{ hostfqdn }}_stop:
  cmd.run:
    - name: /hana/shared/{{ sid|upper }}/HDB{{ instid }}/HDB stop
    - runas: {{ sid }}adm
    - output_logleveldebug: True

{% for port in ports %}
my_hana_{{ hostfqdn }}_stop_hdbrsutil_{{ port }}:
  cmd.run:
    - name:  su - {{ sid }}adm -c "/usr/sap/{{ sid|upper }}/HDB{{ instid }}/exe/hdbrsutil --stop --                                               port 3{{ instid }}{{ port }}"
    - output_logleveldebug: True
    - onchanges:
      - cmd: my_hana_{{ hostfqdn }}_stop
{% endfor %}

my_hana_{{ hostfqdn }}_stop_StopService:
  cmd.run:
    - name: /usr/sap/{{ sid|upper }}/HDB{{ instid }}/exe/sapcontrol -nr {{ instid }} -function Stop                                               Service
    - runas: {{ sid }}adm
    - output_logleveldebug: True
    - onchanges:
      - cmd: my_hana_{{ hostfqdn }}_stop
    - order: last

my_hana_{{ hostfqdn }}_onfail_stop:
  event.send:
    - name: saphana/failed/tostop
    - data:
      status: "Uups HANA stop failed. Alarm."
    - onfail:
      - cmd: my_hana_{{ hostfqdn }}_stop