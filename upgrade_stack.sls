mypkgs:
  pkg.latest:
    - pkgs:
      - libzypp
      - SUSEConnect
      - yast2-pkg-bindings
      - zypper
      - zypper-log
    - only_upgrade: True
