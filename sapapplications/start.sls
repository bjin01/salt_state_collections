{% set hostfqdn = salt['grains.get']('fqdn') %}
{% set clusterip = salt['pillar.get']('sapapps:' + hostfqdn + ':clusterip') %}
{% set APPS = salt['pillar.get']('sapapps:' + hostfqdn + ':installed_apps') %}

fz_sapapps_{{ hostfqdn }}:
  cmd.run:
    - name: ip a | grep {{ clusterip }}

{% for a in APPS %}
{% set application_sid = salt['pillar.get']('sapapps:' + hostfqdn + ':' + a + ':sid') %}
{% set application_instids = salt['pillar.get']('sapapps:' + hostfqdn + ':' + a + ':instances') %}

{% for h in application_instids %}
fz_sapapps_{{ hostfqdn }}_{{ a }}_start_{{ h }}:
  cmd.script:
    - name: salt://fz_sapapps/scripts/sap_start.sh
    - args: {{ application_sid }}adm {{ h }} {{ application_sid|upper }} {{ a }}
    - output_logleveldebug: True
    - require:
      - cmd: fz_sapapps_{{ hostfqdn }}
{% endfor %}
{% endfor %}