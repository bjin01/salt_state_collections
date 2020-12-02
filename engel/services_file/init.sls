{% set myvar = "ENGEL IT" %}
replace_existing_sap_entries:
  file.replace:
    - name: /etc/services
    - pattern: '(^sap.*tcp.*# SAP.*)|(^sap.*tcp.*# R3.*)'
    - repl: ''
    - backup: _backup-by-salt

add_services_entries:
  file.blockreplace:
    - name: /etc/services
    - marker_start: "# START - managed by {{ myvar }} -DO-NOT-EDIT-"
    - marker_end: "# END - managed by {{ myvar }} --"
    - source: salt://engel/services_file/template_services
    - append_if_not_found: True
    - backup: ".backup-blockreplace-salt"
    - append_newline: True

