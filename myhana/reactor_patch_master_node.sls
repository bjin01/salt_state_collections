{% set primary_node = data['data']['primary_node'] %}
{% if primary_node|length %}
prep_hana_master_node_for_patching_{{ primary_node }}:
  runner.state.orchestrate:
    - args:
        - mods: orchestrate.prep_master_node_for_patching
        - pillar:
            event_data: {{ primary_node|json }}
{% endif %}
