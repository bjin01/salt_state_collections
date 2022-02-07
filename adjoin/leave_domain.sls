{% set adjoin_user = salt['pillar.get']('adjoin_user') %}
{% set adjoin_pwd = salt['pillar.get']('adjoin_pwd') %}
{% set adjoin_nodename = salt['grains.get']('nodename') %}

ad_leave_domain:
  cmd.run:
    - name: echo -n {{ adjoin_pwd }} | net ads leave --no-dns-updates -n {{ adjoin_nodename }} -U {{ adjoin_user }}

sssd:
  service.running:
    - enable: True
    - reload: True
    - order: last
    - watch:
      - file: /etc/sssd/sssd.conf

