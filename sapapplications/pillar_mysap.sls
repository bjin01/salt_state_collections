sapapps:
  abc842cz1.mydomain.local:
    installed_apps:
      - application
      - java
    application:
      - sid: sme
      - instances:
        - 41
        - 43
    java:
      - sid: sej
      - instances:
        - 44
        - 45
    clusterip: "134.94.86.110"
  abc842cz2.mydomain.local:
    installed_apps:
      - application
      - java
    application:
      sid: sme
      instances:
        - 41
        - 43
    java:
      sid: sej
      instances:
        - 44
        - 45
    clusterip: "134.94.86.110"

  abc832cz1.mydomain.local:
    installed_apps:
      - application
      - java
    application:
      - sid: pie
      - instances:
        - 10
        - 12
    java:
      - sid: pej
      - instances:
        - 14
        - 15
    clusterip: "134.94.86.151"
  abc832cz2.mydomain.local:
    installed_apps:
      - application
      - java
    application:
      - sid: pie
      - instances:
        - 10
        - 12
    java:
      - sid: pej
      - instances:
        - 14
        - 15
    clusterip: "134.94.86.151"