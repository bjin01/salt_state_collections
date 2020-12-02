{% if 'This minion is now ready to receive further custom sls' in message and data['id'].endswith('.bo2go.home') %}
highstate_run:
  local.state.apply:
    - tgt: {{ data['id'] }}
{% endif %}
