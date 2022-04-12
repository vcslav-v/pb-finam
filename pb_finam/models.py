from sqlalchemy import (Boolean, Column, Date, DateTime, Float, ForeignKey,
                        Integer, Text)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()


class Transaction(Base):
    """Transactions"""

    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True)

    date = Column(Date)
    value = Column(Integer)
    comment = Column(Text)
    date_create = Column(DateTime, onupdate=func.now(), default=func.now())

    currency_id = Column(Integer, ForeignKey('сurrencies.id'))
    currency = relationship('Currency', back_populates='transactions')

    category_id = Column(Integer, ForeignKey('categories.id'))
    category = relationship('Category', back_populates='transactions')


class Currency(Base):
    """Currencies"""

    __tablename__ = 'сurrencies'

    id = Column(Integer, primary_key=True)

    name = Column(Text, unique=True)

    active = Column(Boolean, default=True)

    transactions = relationship('Transaction', back_populates='currency')

    exchange_rate = relationship('ExchangeRate', back_populates='currency')


class ExchangeRate(Base):
    """Exchange Rates"""

    __tablename__ = 'exchange_rates'

    id = Column(Integer, primary_key=True)

    date = Column(Date)
    value = Column(Float)

    currency_id = Column(Integer, ForeignKey('сurrencies.id'))
    currency = relationship('Currency', back_populates='exchange_rate')


class Category(Base):
    """Categories"""

    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)

    name = Column(Text)

    parent_id = Column(Integer, ForeignKey('categories.id'))
    parent = relationship('Category', remote_side=[id])
    children = relationship('Category')
    active = Column(Boolean, default=True)

    transactions = relationship('Transaction', back_populates='category')


class LastStripePaymentId(Base):
    """Last Stripe Payment Id"""

    __tablename__ = 'last_stripe_payment_id'

    id = Column(Integer, primary_key=True)

    value = Column(Text)


class SubscriptionStatistics(Base):
    """SubscriptionStatistics"""

    __tablename__ = 'subscription_statistics'

    id = Column(Integer, primary_key=True)

    date = Column(Date)
    gross_subs_year = Column(Integer)
    gross_subs_month = Column(Integer)
    new_subs_year = Column(Integer)
    new_subs_month = Column(Integer)
    canceled_subs_year = Column(Integer)
    canceled_subs_month = Column(Integer)
