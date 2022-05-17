{% set hostfqdn = salt['grains.get']('fqdn') %}
{% set APPS = salt['pillar.get']('sapapps:' + hostfqdn + ':installed_apps') %}
{% set clusterip = salt['pillar.get']('sapapps:' + hostfqdn + ':clusterip') %}

fz_sapapps_{{ hostfqdn }}:
  cmd.run:
    - name: ip a | grep {{ clusterip }}

{% for a in APPS %}
{% set application_sid = salt['pillar.get']('sapapps:' + hostfqdn + ':' + a + ':sid') %}
{% set application_instids = salt['pillar.get']('sapapps:' + hostfqdn + ':' + a + ':instances') %}

{% for h in application_instids %}
fz_sapapps_{{ hostfqdn }}}_{{ a }}__stop_{{ h }}:
  cmd.script:
    - name: salt://fz_sapapps/scripts/sap_stop.sh
    - args: {{ application_sid }}adm {{ h }} {{ application_sid|upper }} {{ a }}
    - output_logleveldebug: True
    - require:
      - cmd: fz_sapapps_{{ hostfqdn }}
{% endfor %}
{% endfor %}