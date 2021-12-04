import json
import os
from datetime import date, datetime, timedelta

import requests
from loguru import logger

from pb_finam import models, schemas
from pb_finam.db import SessionLocal

BASE_CAT = '__BASE__'
OPEN_EXCHANGE_TOKEN = os.environ.get('OPEN_EXCHANGE_TOKEN') or ''
OPEN_EXCHANGE_ENDPOINT = 'https://openexchangerates.org/api/historical/'
TRANSACTIONS_IN_PAGE = 10


def _add_currencies(session: SessionLocal, currencies: list[str]):
    all_db_currency = session.query(models.Currency).filter_by(active=True).all()
    unique_db_currency_names = set([db_item.name for db_item in all_db_currency])
    unique_setup_currency_names = set(currencies)
    new_currency_names = unique_setup_currency_names - unique_db_currency_names
    remove_currency_names = unique_db_currency_names - unique_setup_currency_names
    for currency in new_currency_names:
        db_currency = session.query(models.Currency).filter_by(name=currency).first()
        if db_currency and not db_currency.active:
            db_currency.active = True
        else:
            new_currency = models.Currency(name=currency)
            session.add(new_currency)
    for currency in remove_currency_names:
        db_currency = session.query(models.Currency).filter_by(name=currency).first()
        if db_currency.transactions:
            db_currency.active = False
        else:
            session.delete(db_currency)
    session.commit()


def _deacive(session: SessionLocal, cattegory: models.Category):
    for child in cattegory.children:
        _deacive(session, child)
    session.refresh(cattegory)
    if cattegory.transactions or cattegory.children:
        cattegory.active = False
    else:
        session.delete(cattegory)
        session.commit()


def _add_cattegory(
    session: SessionLocal,
    category_node: schemas.Node,
    parent: models.Category = None
):
    db_category = session.query(models.Category).filter_by(
        name=category_node.name,
        parent=parent
    ).first()
    if db_category and not db_category.active:
        db_category.active = True
    elif not db_category:
        db_category = models.Category(name=category_node.name, parent=parent)
        session.add(db_category)
        session.commit()

    db_children = session.query(models.Category).filter_by(
        active=True,
        parent=db_category,
    ).all()
    unique_db_children_names = set([db_item.name for db_item in db_children])
    unique_children_names = set([child.name for child in category_node.children])
    remove_currency_names = unique_db_children_names - unique_children_names

    for child_name in remove_currency_names:
        db_child = session.query(models.Category).filter_by(
            name=child_name,
            parent=db_category
        ).first()
        _deacive(session, db_child)

    for child in category_node.children:
        _add_cattegory(session, child, db_category)


@logger.catch
def setup(settings: schemas.Settings):
    with SessionLocal() as session:
        _add_currencies(session, settings.currencies)
        base_category = session.query(models.Category).filter_by(name=BASE_CAT).first()
        if not base_category:
            base_category = models.Category(name=BASE_CAT)
            session.add(base_category)
            session.commit()
        for node in settings.categories:
            _add_cattegory(session, node, base_category)


@logger.catch
def rm_transaction(trans_id: int):
    with SessionLocal() as session:
        db_transaction = session.query(models.Transaction).filter_by(id=trans_id).first()
        session.delete(db_transaction)
        session.commit()


@logger.catch
def add_transaction(transaction: schemas.Transaction):
    with SessionLocal() as session:
        if transaction.id:
            db_transaction = session.query(models.Transaction).filter_by(id=transaction.id).first()
            if not db_transaction:
                raise ValueError('It transaction is wrong')
            db_transaction.date = transaction.date,
            db_transaction.value = transaction.value,
            db_transaction.comment = transaction.comment,
        else:
            db_transaction = models.Transaction(
                date=transaction.date,
                value=transaction.value,
                comment=transaction.comment,
            )
        currency = session.query(models.Currency).filter_by(id=transaction.currency_id).first()
        if not currency:
            raise ValueError('Currency is not exist')
        db_transaction.currency = currency
        category = session.query(models.Category).filter_by(id=transaction.category_id).first()
        if not category:
            raise ValueError('Category is not exist')
        db_transaction.category = category
        _check_exchange_rate(session, transaction.date)
        session.add(db_transaction)
        session.commit()


@logger.catch
def get_transaction(trans_id) -> schemas.Transaction:
    with SessionLocal() as session:
        db_transaction = session.query(models.Transaction).filter_by(id=int(trans_id)).first()
        if db_transaction:
            category_id_path = _get_category_id_path(db_transaction.category)
            category_id_path.reverse()
            return schemas.Transaction(
                id=db_transaction.id,
                date=db_transaction.date,
                value=db_transaction.value,
                comment=db_transaction.comment,
                currency_id=db_transaction.currency_id,
                category_id=db_transaction.category_id,
                category_id_path=category_id_path,
            )


@logger.catch
def get_transactions(page_data: schemas.GetTransactionPage) -> schemas.TransactionPage:
    with SessionLocal() as session:
        result = schemas.TransactionPage()
        if page_data.page:
            start = page_data.page * TRANSACTIONS_IN_PAGE
            end = start + TRANSACTIONS_IN_PAGE
        else:
            start = 0
            end = TRANSACTIONS_IN_PAGE

        db_transactions = session.query(
            models.Transaction
        ).filter(
            models.Transaction.date <= page_data.from_date
        ).order_by(
            models.Transaction.date.desc()
        ).order_by(
            models.Transaction.date_create.desc()
        ).slice(start, end)
        for db_transaction in db_transactions:
            category_path = _get_category_path(db_transaction.category)
            category_path.reverse()
            result.rows.append(schemas.PageTransaction(
                id=db_transaction.id,
                date=db_transaction.date.strftime('%d-%m-%Y'),
                value=f'{round(db_transaction.value/100, 2)} {db_transaction.currency.name}',
                comment=db_transaction.comment,
                base_category=category_path[0],
                category='/'.join(category_path[1:]),
            ))
        return result


def _get_category_id_path(category: models.Category):
    result = []
    if category.name != BASE_CAT:
        result.append(category.id)
        result.extend(_get_category_id_path(category.parent))
    return result


def _get_category_path(category: models.Category):
    result = []
    if category.name != BASE_CAT:
        result.append(category.name)
        result.extend(_get_category_path(category.parent))
    return result


def _check_exchange_rate(session: SessionLocal, date: datetime.date):
    currencies = session.query(models.Currency).all()
    for currency in currencies:
        exchange_rate = session.query(models.ExchangeRate).filter_by(
            date=date,
            currency=currency,
        ).first()
        if not exchange_rate:
            _add_exchange_rates(session, date)
            break


def _add_exchange_rates(session: SessionLocal, date: datetime.date):
    resp = requests.get(
        f'{OPEN_EXCHANGE_ENDPOINT}{date.isoformat()}.json?app_id={OPEN_EXCHANGE_TOKEN}'
    )
    exchange_rates = json.loads(resp.content)['rates']
    currencies = session.query(models.Currency).all()
    for currency in currencies:
        exchange_rate = session.query(models.ExchangeRate).filter_by(
            date=date,
            currency=currency,
        ).first()
        if not exchange_rate:
            exchange_rate = models.ExchangeRate(
                date=date,
                currency=currency,
            )
            session.add(exchange_rate)
        exchange_rate.value = exchange_rates[currency.name]
    session.commit()


@logger.catch
def get_category_tree(db_category: models.Category = None) -> schemas.Items:
    with SessionLocal() as session:
        if not db_category:
            db_category = session.query(models.Category).filter_by(
                name=BASE_CAT,
            ).first()
        result = schemas.Node(
            name=db_category.name,
            id=db_category.id
        )
        for child in db_category.children:
            result.children.append(get_category_tree(child))
    return result


@logger.catch
def get_сurrencies() -> schemas.Items:
    with SessionLocal() as session:
        result = schemas.Items()
        db_сurrencies = session.query(models.Currency).filter_by(
            active=True,
        ).all()
        for db_сurrency in db_сurrencies:
            result.items.append(
                schemas.Item(
                    name=db_сurrency.name,
                    id=db_сurrency.id
                )
            )
    return result


@logger.catch
def get_short_stat() -> schemas.ShortStat:
    with SessionLocal() as session:
        today = datetime.now().date()
        start_month = date(today.year, today.month, 1)
        past_month = start_month - timedelta(days=1)
        start_past_month = date(past_month.year, past_month.month, 1)
        if past_month.day > today.day:
            check_date_past_month = date(past_month.year, past_month.month, today.day)
        else:
            check_date_past_month = past_month

        db_trans_cur = session.query(models.Transaction).filter(
            models.Transaction.date >= start_month
        ).filter(
            models.Transaction.date <= today
        ).all()
        db_trans_past = session.query(models.Transaction).filter(
            models.Transaction.date >= start_past_month
        ).filter(
            models.Transaction.date <= check_date_past_month
        ).all()
        db_income = session.query(models.Category).filter_by(name='Income').first()
        income_cats_id = _get_children_ids(db_income)
        db_expense = session.query(models.Category).filter_by(name='Expense').first()
        expense_cats_id = _get_children_ids(db_expense)
        income = 0
        expense = 0
        profit = 0
        for trans in db_trans_cur:
            exchange_rate = session.query(
                models.ExchangeRate
            ).filter_by(
                date=trans.date
            ).filter_by(
                currency=trans.currency
            ).first()
            if trans.category_id in income_cats_id:
                income += int((trans.value / 100) * exchange_rate.value)
            elif trans.category_id in expense_cats_id:
                expense += int((trans.value / 100) * exchange_rate.value)
        profit = income - expense
        now_month = schemas.MonthShortStat(
            name=today.strftime("%B"),
            income=income,
            expense=expense,
            profit=profit,
        )
        income = 0
        expense = 0
        profit = 0
        for trans in db_trans_past:
            exchange_rate = session.query(
                trans.currency.exchange_rate
            ).filter_by(date=trans.date).first()
            if trans.category_id in income_cats_id:
                income += int((trans.value / 100) * exchange_rate.value)
            elif trans.category_id in expense_cats_id:
                expense += int((trans.value / 100) * exchange_rate.value)
        profit = income - expense
        pst_month = schemas.MonthShortStat(
            name=past_month.strftime("%B"),
            income=income,
            expense=expense,
            profit=profit,
        )
        return schemas.ShortStat(
            now_month=now_month,
            past_month=pst_month,
        )


def _get_children_ids(cat: models.Category) -> list[int]:
    result = [cat.id]
    for child in cat.children:
        result.extend(_get_children_ids(child))
    return result
