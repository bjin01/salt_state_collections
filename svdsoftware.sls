svdtest_1:
  pkg.installed:
    - pkgs:
      - vim
      - telnet
      - openssh

forbidden_software:
  pkg.removed:
    - pkgs:
      - samba

