#this sls is for onboarding any minions which key has already been accepted by suse manager but not assigned a activation key yet. This sls should cause minion to execute the bootstrap.sh executed on the new minion.
#include:
#  - certs.SLES12

{% set osversion = salt['grains.get']('oscodename', '') %}

{% if osversion == 'SUSE Linux Enterprise Server 12 SP1' %} 
susemanagerconf:
    file.managed:
      - name: /etc/salt/minion.d/susemanager.conf
      - source: salt://mybootstrap/susemanager-sles12sp1.conf
      - create: True
      - template: jinja
      - saltenv: base
      - skip_verify: True
      - user: root
      - group: root
      - mode: 640

salt://mybootstrap/bootstrap-sles12sp1-salt.sh:
  cmd.script:
    - runas: root

rhnorgcert1:
    file.managed:
      - name: /etc/pki/trust/anchors/RHN-ORG-TRUSTED-SSL-CERT
      - source: salt://mybootstrap/RHN-ORG-TRUSTED-SSL-CERT
      - create: True
      - template: jinja
      - saltenv: base
      - skip_verify: True
      - user: root
      - group: root
      - mode: 640

update-ca-certificates:
  cmd.wait:
    - name: /usr/sbin/update-ca-certificates
    - user: root
    - watch:
      - file: /etc/pki/trust/anchors/RHN-ORG-TRUSTED-SSL-CERT
{% endif %}

{% if osversion == 'SUSE Linux Enterprise Server 12 SP2' %} 
susemanagerconf:
    file.managed:
      - name: /etc/salt/minion.d/susemanager.conf
      - source: salt://mybootstrap/susemanager-sles12sp2.conf
      - create: True
      - template: jinja
      - saltenv: base
      - skip_verify: True
      - user: root
      - group: root
      - mode: 640

salt://mybootstrap/bootstrap-sles12sp2-salt.sh:
  cmd.script:
    - runas: root

rhnorgcert2:
    file.managed:
      - name: /etc/pki/trust/anchors/RHN-ORG-TRUSTED-SSL-CERT
      - source: salt://mybootstrap/RHN-ORG-TRUSTED-SSL-CERT
      - create: True
      - template: jinja
      - saltenv: base
      - skip_verify: True
      - user: root
      - group: root
      - mode: 640

update-ca-certificates:
  cmd.wait:
    - name: /usr/sbin/update-ca-certificates
    - user: root
    - watch:
      - file: /etc/pki/trust/anchors/RHN-ORG-TRUSTED-SSL-CERT
{% endif %}

{% if osversion == 'SUSE Linux Enterprise Server for SAP Applications 12 SP2' %} 
susemanagerconf:
    file.managed:
      - name: /etc/salt/minion.d/susemanager.conf
      - source: salt://mybootstrap/susemanager-sles4sap.conf
      - create: True
      - template: jinja
      - saltenv: base
      - skip_verify: True
      - user: root
      - group: root
      - mode: 640

salt://mybootstrap/bootstrap-sles4sap-salt.sh:
  cmd.script:
    - runas: root

rhnorgcert2:
    file.managed:
      - name: /etc/pki/trust/anchors/RHN-ORG-TRUSTED-SSL-CERT
      - source: salt://mybootstrap/RHN-ORG-TRUSTED-SSL-CERT
      - create: True
      - template: jinja
      - saltenv: base
      - skip_verify: True
      - user: root
      - group: root
      - mode: 640

update-ca-certificates:
  cmd.wait:
    - name: /usr/sbin/update-ca-certificates
    - user: root
    - watch:
      - file: /etc/pki/trust/anchors/RHN-ORG-TRUSTED-SSL-CERT
{% endif %}
