import json
import os
from datetime import datetime, timedelta
import re
import requests

import stripe

from pb_finam import schemas
from pb_finam import db_tools

STRIPE_CATEGORIES = os.environ.get('STRIPE_CATEGORIES', '{}')
STRIPE_CATEGORIES = json.loads(STRIPE_CATEGORIES)
RE_LIFETIME = re.compile('Plus Lifetime')


def get_stripe_transactions() -> tuple[str, dict]:
    stripe.api_key = os.environ.get('STRIPE_API_KEY', '')
    last_payment = db_tools.get_last_stripe_payment_id()
    payments = stripe.PaymentIntent.list(ending_before=last_payment)
    work_payment_date = datetime.fromtimestamp(0)
    payments_data = {}
    next_last_payment = ''
    today = datetime.utcnow().date()
    amount_new_lifetime_yesterday = 0
    for payment in payments.auto_paging_iter():
        if payment['invoice']:
            invoice = stripe.Invoice.retrieve(payment['invoice'])
            product = stripe.Product.retrieve(invoice['lines']['data'][0]['plan']['product'])

            payment_amount = payment['amount']
            payment_date_creation = datetime.fromtimestamp(payment['created']).date()
            product_name = product['name']
        elif payment['charges']['data'] and payment['charges']['data'][0]['paid']:
            receipt = requests.get(payment['charges']['data'][0]['receipt_url'])
            if RE_LIFETIME.findall(receipt.text):
                product_name = 'Plus Lifetime'
                amount_new_lifetime_yesterday += 1
            payment_amount = payment['amount']
            payment_date_creation = datetime.fromtimestamp(payment['created']).date()
            product_name = 'Premium'
        else:
            continue

        if work_payment_date != payment_date_creation:
            work_payment_date = payment_date_creation
            payments_data[work_payment_date.strftime('%Y-%m-%d')] = {
                'Plus Lifetime': 0,
                'Plus Yearly': 0,
                'Plus Monthly': 0,
                'Premium': 0
            }
        if today != payment_date_creation:
            next_last_payment = payment['id']
            payments_data[
                payment_date_creation.strftime('%Y-%m-%d')
            ][product_name] += payment_amount
    return (next_last_payment, payments_data, amount_new_lifetime_yesterday)


def save_stripe_transactions(next_last_payment: str, payments_data: dict):
    currencies = db_tools.get_сurrencies()
    for currency in currencies.items:
        if currency.name.lower() == 'usd':
            currency_id = currency.id
            break
    for payment_date, payments in payments_data.items():
        for payment_type, payment_amount in payments.items():
            if payment_amount == 0:
                continue
            transaction = schemas.Transaction(
                date=payment_date,
                value=payment_amount,
                comment='',
                currency_id=currency_id,
                category_id=STRIPE_CATEGORIES[payment_type],
            )
            db_tools.add_transaction(transaction)
    db_tools.set_last_stripe_payment_id(next_last_payment)


def get_stripe_subscriptions() -> tuple[schemas.SubsStat]:
    stripe.api_key = os.environ.get('STRIPE_API_KEY', '')
    amount_active_subs = schemas.SubsStat()
    amount_canceled_subs = schemas.SubsStat()
    amount_new_subs = schemas.SubsStat()
    year_gross_usd = 0
    month_gross_usd = 0
    yesterday = datetime.utcnow().date() - timedelta(days=1)

    active_subs = stripe.Subscription.list(status='active')
    for active_sub in active_subs.auto_paging_iter():
        interval = active_sub['items']['data'][0]['plan']['interval']
        price = active_sub['items']['data'][0]['price']['unit_amount_decimal']
        if interval == 'year':
            amount_active_subs.year += 1
            year_gross_usd += price
        elif interval == 'month':
            month_gross_usd += price
            amount_active_subs.month += 1
        if datetime.fromtimestamp(active_sub['created']).date() == yesterday:
            if interval == 'year':
                amount_new_subs.year += 1
            elif interval == 'month':
                amount_new_subs.month += 1

    ended_subs = stripe.Subscription.list(status='canceled')
    for ended_sub in ended_subs.auto_paging_iter():
        interval = ended_sub['items']['data'][0]['plan']['interval']
        if datetime.fromtimestamp(ended_sub['canceled_at']).date() == yesterday:
            if interval == 'year':
                amount_canceled_subs.year += 1
            elif interval == 'month':
                amount_canceled_subs.month += 1
    return (
        yesterday,
        amount_active_subs,
        amount_new_subs,
        amount_canceled_subs,
        month_gross_usd,
        year_gross_usd,
    )
