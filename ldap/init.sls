ldapsoftware:
  pkg.installed:
    - pkgs:
      - krb5-client
      - samba-client
      - openldap2-client
      - sssd-ad

service_nscd:
  service.dead:
    - name: nscd
    - enable: false

service_nscd_disable:
  service.disabled:
    - name: nscd

service_sssd:
   service.running:
      - name: sssd
      - enable: True
      - watch:
         - pkg: krb5-client
         - file: /etc/sssd/sssd.conf
      - onchanges:
        - file: config_files_sssd

config_files_krb5:
   file.managed:
      - name: /etc/krb5.conf
      - source: salt://ldap/krb5.conf
      - create: True
      - template: jinja
      - saltenv: base
      - skip_verify: True
      - user: root
      - group: root
      - mode: 640
      - require:
         - pkg: krb5-client


config_files_sssd:
   file.managed:
      - name: /etc/sssd/sssd.conf 
      - source: salt://ldap/sssd.conf
      - create: True
      - template: jinja
      - saltenv: base
      - skip_verify: True
      - user: root
      - group: root
      - mode: 640
      - require:
         - pkg: sssd-ad


config_files_nsswitch:
   file.managed:
      - name: /etc/nsswitch.conf 
      - source: salt://ldap/nsswitch.conf
      - create: True
      - template: jinja
      - saltenv: base
      - skip_verify: True
      - user: root
      - group: root
      - mode: 640
      - require:
         - pkg: krb5-client

config_files_ldapconf:
   file.managed:
      - name: /etc/openldap/ldap.conf 
      - source: salt://ldap/ldap.conf
      - create: True
      - template: jinja
      - saltenv: base
      - skip_verify: True
      - user: root
      - group: root
      - mode: 640
      - require:
         - pkg: openldap2-client
