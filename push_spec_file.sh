snowsql -c spcsdemo -q "USE DATABASE DEMOS; USE SCHEMA GEN_EMAILS; PUT file:///Users/andrewevans/spcs/SnowparkContainerServices-Tutorials/email-demo/email_demo_spec.yaml @EMAIL_DEMO_STAGE AUTO_COMPRESS=FALSE OVERWRITE=TRUE;"

