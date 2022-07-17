{% set node =  data['data']['node'] %}
{% if data['data']['cluster_idle'] and node|length %}

set_msl_maint_off_{{ node }}:
  cmd.bocrm.off_msl_maintenance:
    - tgt: {{ node }}
    - args:
      - msl_resource_name: msl_SAPHana_BJK_HDB00
{% endif %}
