{% set hostname = salt['grains.get']('fqdn') %}
{% if hostname|length %}
start_pacemaker_{{ hostname }}:
  module.run:
    - name: bocrm.start_pacemaker

check_for_clusterstate_idle_{{ hostname }}:
  module.run:
    - name: bocrm.wait_for_cluster_idle
    - interval: 60
    - timeout: 10
    - require:
      - module: start_pacemaker_{{ hostname }}
{% endif %}

{% set hana_info = salt['grains.get']('hana_info') %}
{% if hana_info.diskless_node|length %}
send_event_diskless_node_finished_{{ hana_info.diskless_node }}:
  event.send:
    - name: suma/cluster/diskless_node/started/ready_to_patch_master_node
    - data:
        message: "diskless node pacemaker started and cluster state is idle, ready to continue with master node"
        node: {{ hana_info }} 
        cluster_idle: True
    - require:
      - module: check_for_clusterstate_idle_{{ hostname }}
{% endif %}
