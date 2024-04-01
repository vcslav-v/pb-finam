import os

# google cloud auth
AUTH_FILE_PATH = os.environ.get('AUTH_FILE_PATH', '')
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = AUTH_FILE_PATH
with open(AUTH_FILE_PATH, 'w') as f:
    f.write(
        os.environ.get(
            'AUTH_FILE_DATA',
            ''
        )
    )

# bigquery
BQ_PROJECT = os.environ.get('BQ_PROJECT', '')
BQ_DATASET = os.environ.get('BQ_DATASET', '')
