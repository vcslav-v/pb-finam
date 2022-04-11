release: alembic upgrade head
clock: python pb_finam/scheluder.py
web: gunicorn -w 4 -k uvicorn.workers.UvicornWorker pb_finam.main:app