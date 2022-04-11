from apscheduler.schedulers.blocking import BlockingScheduler
from loguru import logger
from pb_finam import stripe_connector


sched = BlockingScheduler()


@logger.catch
@sched.scheduled_job('cron', hour=13)
def add_stripe_transactions():
    logger.info('Add stripe transactions')
    next_last_payment, payments_data = stripe_connector.get_stripe_transactions()
    stripe_connector.save_stripe_transactions(next_last_payment, payments_data)


if __name__ == "__main__":
    sched.start()
