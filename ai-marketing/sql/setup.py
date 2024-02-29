import click
from aimarketing.snowflake_utils import get_snowpark_session

from snowflake.snowpark.types import (
    StructType,
    StructField,
    StringType,
    DateType,
    IntegerType,
)

from pathlib import Path


@click.command()
@click.option("--drop-tables", is_flag=True, help="Drop all tables")
def main(drop_tables):
    session = get_snowpark_session()

    session.sql("create schema if not exists DEMOS.AI_MARKETING;").collect()

    session.sql("drop table if exists DEMOS.AI_MARKETING.SALES_CONTACTS").collect()
    session.sql("create or replace temporary stage temp_stage").collect()
    session.file.put(
        str(Path("extraordinary_events.csv").absolute()),
        "@temp_stage/extraordinary_events",
        overwrite=True,
    )
    user_schema = StructType(
        [
            StructField("UID", IntegerType()),
            StructField("COMPANY_NAME", StringType()),
            StructField("CONTACT_NAME", StringType()),
            StructField("CONTACT_EMAIL", StringType()),
            StructField("INDUSTRY", StringType()),
            StructField("PREVIOUS_EVENT", StringType()),
            StructField("PREVIOUS_EVENT_DATE", DateType()),
            StructField("NOTES", StringType()),
        ]
    )

    session.sql("drop table if exists copied_into_table").collect()
    df = (
        session.read.schema(user_schema)
        .options(
            dict(SKIP_HEADER=1, FIELD_OPTIONALLY_ENCLOSED_BY='"', FIELD_DELIMITER=",")
        )
        .csv("@temp_stage/extraordinary_events")
    )
    df.copy_into_table("DEMOS.AI_MARKETING.SALES_CONTACTS", force=True)

    if drop_tables:
        session.sql(
            "drop table if exists DEMOS.AI_MARKETING.GPT_EMAIL_PROMPTS"
        ).collect()

    session.sql(
        """
    create TABLE if not exists DEMOS.AI_MARKETING.GPT_EMAIL_PROMPTS (
        SESSION_ID string,
        UID NUMBER(38,0),
        CONTACT_EMAIL string,
        CAMPAIGN_NAME string,
        SYSTEM_PROMPT string,
        USER_PROMPT string,
        EMAIL string,
        TIMESTAMP TIMESTAMP_NTZ(9)
    );"""
    ).collect()

    session.sql(
        """create or replace view DEMOS.AI_MARKETING.GPT_EMAIL_PROMPTS_LATEST(
            SESSION_ID, UID, CONTACT_EMAIL, CAMPAIGN_NAME, SYSTEM_PROMPT, USER_PROMPT, EMAIL, TIMESTAMP
        ) as
        SELECT SESSION_ID, UID, CONTACT_EMAIL, CAMPAIGN_NAME, SYSTEM_PROMPT, USER_PROMPT, EMAIL, TIMESTAMP
        FROM (
            SELECT *,
                ROW_NUMBER() OVER (PARTITION BY UID ORDER BY TIMESTAMP DESC) AS rn
            FROM DEMOS.AI_MARKETING.GPT_EMAIL_PROMPTS
        ) t
        WHERE rn = 1;"""
    ).collect()


if __name__ == "__main__":
    main()
