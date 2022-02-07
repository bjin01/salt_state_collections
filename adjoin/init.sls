{% set adjoin_user = salt['pillar.get']('adjoin_user') %}
{% set adjoin_pwd = salt['pillar.get']('adjoin_pwd') %}
{% set adjoin_nodename = salt['grains.get']('nodename') %}

adjoin_packages:
  pkg.installed:
    - pkgs:
      - sssd
      - sssd-ad
      - krb5-client
 
/etc/samba/smb.conf:
  file.managed:
    - source: salt://adjoin/configs/smb.conf
    - source_hash: fb266fd9dd44ef061576248126c76ee3

/etc/sssd/sssd.conf:
  file.managed:
    - source: salt://adjoin/configs/sssd.conf
    - source_hash: 8e437d4a8af995838b4d9562499a057b

/etc/krb5.conf:
  file.managed:
    - source: salt://adjoin/configs/krb5.conf
    - source_hash: 08d566dcce11ccdb046a99a67d3e56ff

/etc/nsswitch.conf:
  file.managed:
    - source: salt://adjoin/configs/nsswitch.conf
    - source_hash: 7d7a775a0c0c9f39113efb199d13d9c2

disable_nscd:
  service.disabled:
    - name: nscd 

stop_nscd:
  service.dead:
    - name: nscd 

ad_join_now:
  cmd.run:
    - name: echo -n {{ adjoin_pwd }} | net ads join --no-dns-updates -n {{ adjoin_nodename }} -U {{ adjoin_user }}

pam_config_sss:
  cmd.run:
    - name: pam-config -a --sss

pam_config_mkhomedir:
  cmd.run:
    - name: pam-config -a --mkhomedir

sssd:
  service.running:
    - enable: True
    - reload: True
    - order: last
    - watch:
      - file: /etc/sssd/sssd.conf

