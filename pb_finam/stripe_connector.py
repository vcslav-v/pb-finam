import json
import os
from datetime import datetime

import stripe

from pb_finam import schemas
from pb_finam import db_tools

STRIPE_CATEGORIES = os.environ.get('STRIPE_CATEGORIES', '{}')
STRIPE_CATEGORIES = json.loads(STRIPE_CATEGORIES)


def get_stripe_transactions() -> tuple[str, dict]:
    stripe.api_key = os.environ.get('STRIPE_API_KEY', '')
    last_payment = db_tools.get_last_stripe_payment_id()
    payments = stripe.PaymentIntent.list(ending_before=last_payment)
    work_payment_date = datetime.fromtimestamp(0)
    payments_data = {}
    next_last_payment = ''
    today = datetime.utcnow().date()
    for payment in payments.auto_paging_iter():
        if payment['invoice']:
            invoice = stripe.Invoice.retrieve(payment['invoice'])
            product = stripe.Product.retrieve(invoice['lines']['data'][0]['plan']['product'])

            payment_amount = payment['amount']
            payment_date_creation = datetime.fromtimestamp(payment['created']).date()
            product_name = product['name']
        elif payment['charges']['data'] and payment['charges']['data'][0]['paid']:
            payment_amount = payment['amount']
            payment_date_creation = datetime.fromtimestamp(payment['created']).date()
            product_name = 'Premium'
        else:
            continue

        if work_payment_date != payment_date_creation:
            work_payment_date = payment_date_creation
            payments_data[work_payment_date.strftime('%Y-%m-%d')] = {
                'Plus Yearly': 0,
                'Plus Monthly': 0,
                'Premium': 0
            }
        if today != payment_date_creation:
            next_last_payment = payment['id']
            payments_data[
                payment_date_creation.strftime('%Y-%m-%d')
            ][product_name] += payment_amount
    return (next_last_payment, payments_data)


def save_stripe_transactions(next_last_payment: str, payments_data: dict):
    currencies = db_tools.get_сurrencies()
    for currency in currencies.items:
        if currency.name.lower() == 'usd':
            currency_id = currency.id
            break
    for payment_date, payments in payments_data.items():
        for payment_type, payment_amount in payments.items():
            if payment_amount < 0:
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
