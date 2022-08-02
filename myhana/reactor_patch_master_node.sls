{% set member_nodes = salt['grains.get']('hana_info:cluster_nodes') %}
{% set node = salt['grains.get']('id') %}
check_sr_status_{{ node }}:
  module.run:
    - name: bocrm.check_sr_status

{% for i in member_nodes %}
get_master_node_from_{{ i }}:
  grains.exists:
    - name: "hana_info:hana_primary"
    - require:
      - module: check_sr_status_{{ node }}

send_event_ready_to_patch_next_{{ i }}:
  event.send:
    - name: suma/cluster/patch_master_node_now
    - data:
        message: "patch master node"
        master_node: {{ i }} 
    - require:
      - grains: get_master_node_from_{{ i }}
{% endfor %}
