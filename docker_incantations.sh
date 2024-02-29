docker build --rm --platform linux/amd64 -t email_demo:0.1 -f Dockerfile .
docker tag email_demo:0.1 phdatapartner-scs.registry.snowflakecomputing.com/demos/gen_emails/email_demo_repository/email_demo:0.1
docker push phdatapartner-scs.registry.snowflakecomputing.com/demos/gen_emails/email_demo_repository/email_demo:0.1

