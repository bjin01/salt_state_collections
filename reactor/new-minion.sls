{% if 'act' in data and data['act'] == 'pend' and data['id'].startswith('z') %}
minion_key_accept:
  wheel.key.accept:
    - match: {{ data['id'] }} 
{% endif %}
