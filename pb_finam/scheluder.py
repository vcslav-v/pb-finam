from loguru import logger
from pb_finam import db_tools, stripe_connector


@logger.catch
def add_stripe_transactions():
    logger.info('Add stripe transactions')
    next_last_payment, payments_data = stripe_connector.get_stripe_transactions()
    if next_last_payment and payments_data:
        stripe_connector.save_stripe_transactions(next_last_payment, payments_data)


@logger.catch
def add_stripe_subscriptions():
    logger.info('Add stripe subscriptions')
    yesterday, amount_active_subs, amount_new_subs, amount_canceled_subs = (
        stripe_connector.get_stripe_subscriptions()
    )
    db_tools.add_subscription_stat(
        yesterday,
        amount_active_subs,
        amount_new_subs,
        amount_canceled_subs,
    )


if __name__ == '__main__':
    add_stripe_transactions()
    add_stripe_subscriptions()
