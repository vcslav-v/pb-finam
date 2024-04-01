from google.cloud import bigquery
from pb_finam import config, db_tools


def sync():
    bq_client = bigquery.Client()
    for table_name, df in db_tools.get_all_db_data():
        table_id = f'{config.BQ_PROJECT}.{config.BQ_DATASET}.{table_name}'
        job_config = bigquery.LoadJobConfig(
            write_disposition='WRITE_TRUNCATE',
            source_format=bigquery.SourceFormat.PARQUET,
        )
        bq_client.load_table_from_dataframe(df, table_id, job_config=job_config)


if __name__ == '__main__':
    sync()
