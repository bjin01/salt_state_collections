{% for user in salt['pillar.get']('delete_users', []) %}
{{ user }}:
  user.absent:
    - purge: True
    - force: True
{% endfor %}
