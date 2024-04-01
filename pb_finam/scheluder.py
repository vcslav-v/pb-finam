from loguru import logger
from pb_finam import db_tools, stripe_connector, pb_connector, bq_sync
from datetime import datetime, timedelta


@logger.catch
def add_stripe_transactions():
    logger.info('Add stripe transactions')
    (
        next_last_payment,
        payments_data,
        amount_new_lifetime_yesterday,
    ) = stripe_connector.get_stripe_transactions()
    if next_last_payment and payments_data:
        stripe_connector.save_stripe_transactions(next_last_payment, payments_data)
    add_stripe_subscriptions(amount_new_lifetime_yesterday)


@logger.catch
def add_stripe_subscriptions(
    amount_new_lifetime_yesterday: int
):
    logger.info('Add stripe subscriptions')
    (
        yesterday,
        amount_active_subs,
        amount_new_subs,
        amount_canceled_subs,
        month_gross_usd,
        year_gross_usd,
    ) = (
        stripe_connector.get_stripe_subscriptions()
    )
    amount_new_subs.lifetime = amount_new_lifetime_yesterday
    db_tools.add_subscription_stat(
        yesterday,
        month_gross_usd,
        year_gross_usd,
        amount_active_subs,
        amount_new_subs,
        amount_canceled_subs,
    )


@logger.catch
def renew_subs():
    subs_site_stat = pb_connector.get_subscriptions()
    yesterday = datetime.utcnow().date() - timedelta(days=1)
    db_tools.add_subscription_stat(
        yesterday,
        subs_site_stat,
    )


if __name__ == '__main__':
    # add_stripe_transactions()
    renew_subs()
    bq_sync.sync()
