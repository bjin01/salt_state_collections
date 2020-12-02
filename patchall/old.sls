{% if grains['fully_update_this_box'] == 'True' %}
update_all:
  cmd.run:
    - name: /usr/bin/zypper --non-interactive --no-refresh patch 
{% endif %}
