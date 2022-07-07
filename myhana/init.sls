precheck_myhana_test:
  crmhana.precheck:
    - name: hana


maint_hana-secondary:
  crmhana.maint_secondary:
    - name: hana
    - msl_resource: msl_SAPHana_BJK_HDB00
    - require:
      - crmhana: precheck_myhana_test
