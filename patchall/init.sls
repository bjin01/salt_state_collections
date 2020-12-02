{% if grains['fully_update_this_box'] %}
update_all:
  cmd.run:
    - name: /usr/bin/zypper --non-interactive --no-refresh patch --auto-agree-with-licenses --force --force-resolution 
{% endif %}
