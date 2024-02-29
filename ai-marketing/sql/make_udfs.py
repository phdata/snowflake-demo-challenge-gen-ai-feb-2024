from aimarketing.snowflake_utils import get_snowpark_session
import click


@click.command()
def main():
    session = get_snowpark_session()

    session.sql("create or replace stage udf_stage").collect()
    session.udf.register_from_file(
        file_path="aimarketing/date_utils.py",
        func_name="humanize_date",
        name="humanize_date",
        is_permanent=True,
        replace=True,
        stage_location="@udf_stage",
    )
    session.file.put(
        "aimarketing/utils.py",
        "@udf_stage/submit_gpt_prompt",
        overwrite=True,
    )

    print(
        session.sql(
            "select humanize_date(date_from_parts(2022,12,1), date_from_parts(2023,5,22)) as event;"
        ).collect()
    )


if __name__ == "__main__":
    main()
