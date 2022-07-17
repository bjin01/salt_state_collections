{% set node =  data['data']['node'] %}
{% if data['data']['reboot'] and node|length %}
adsf_start_pacemaker_{{ node }}:
  cmd.bocrm.start_pacemaker:
    - tgt: {{ node }}

loop_wait_for_cluster_idle_state_{{ node }}:
  cmd.bocrm.wait_for_cluster_idle:
    - tgt: {{ node }}
    - args:
      - interval: 20
      - timeout: 300

{% endif %}
