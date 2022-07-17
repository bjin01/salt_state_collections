precheck_myhana_test:
  crmhana.precheck:
    - name: hana


maint_hana-secondary:
  crmhana.maint_secondary:
    - name: hana
    - msl_resource: msl_SAPHana_BJK_HDB00
    - require:
      - crmhana: precheck_myhana_test

{% set secondary_hostname = salt['grains.get']('hana_secondary') %}
{% if secondary_hostname is defined and secondary_hostname|length %}
send_event_{{ secondary_hostname }}:
  event.send:
    - name: suma/hana/secondary/patch/ready
    - data:
      secondary_node: {{ secondary_hostname }}
{% endif %}

