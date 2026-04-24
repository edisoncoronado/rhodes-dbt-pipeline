// dbt was having issues connecting due to MFA
USE ROLE ACCOUNTADMIN;

CREATE OR REPLACE AUTHENTICATION POLICY dbt_auth_policy
  MFA_ENROLLMENT = OPTIONAL
  CLIENT_TYPES = ('ALL');

ALTER USER edisoncoronado
  SET AUTHENTICATION POLICY dbt_auth_policy;