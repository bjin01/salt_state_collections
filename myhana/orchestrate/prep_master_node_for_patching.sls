{% set primary_node = salt['pillar.get']('event_data') %}
prep_hana_master_node_{{ primary_node[0] }}:
  salt.state:
    - tgt: {{ primary_node[0] }}*
    - sls:
      - myhana.testit

