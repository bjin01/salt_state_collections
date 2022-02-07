{% set adjoin_user = salt['pillar.get']('adjoin_user') %}
{% set adjoin_pwd = salt['pillar.get']('adjoin_pwd') %}

kinit_cmd:
  cmd.run:
    - name: echo -n {{ adjoin_pwd }} {{ adjoin_user }}
