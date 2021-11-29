from sqlalchemy import Column, Date, ForeignKey, Integer, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Transaction(Base):
    """Transactions"""

    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True)

    date = Column(Date)
    value = Column(Integer)
    comment = Column(Text)

    currency_id = Column(Integer, ForeignKey('сurrencies.id'))
    currency = relationship('Currency', back_populates="transactions")

    exchange_rate_id = Column(Integer, ForeignKey('exchange_rates.id'))
    exchange_rate = relationship('ExchangeRate', back_populates="transactions")

    category_id = Column(Integer, ForeignKey('categories.id'))
    category = relationship('Category', back_populates="transactions")


class Currency(Base):
    """Currencies"""

    __tablename__ = 'сurrencies'

    id = Column(Integer, primary_key=True)

    name = Column(Text)

    transactions = relationship('Transaction', back_populates="currency")


class ExchangeRate(Base):
    """Exchange Rates"""

    __tablename__ = 'exchange_rates'

    id = Column(Integer, primary_key=True)

    date = Column(Date)
    usdrub = Column(Float)
    eurrub = Column(Float)
    eurusd = Column(Float)

    transactions = relationship('Transaction', back_populates="exchange_rate")


class Category(Base):
    """Categories"""

    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)

    name = Column(Text)

    parent_id = Column(Integer, ForeignKey('categories.id'))
    parent = relationship('Category', remote_side=[id])
    children = relationship('Category')

    transactions = relationship('Transaction', back_populates="category")

    direct_id = Column(Integer, ForeignKey('directs.id'))
    direct = relationship('Direct', back_populates="categories")


class Direct(Base):
    """Categoriy's direct"""

    __tablename__ = 'directs'

    id = Column(Integer, primary_key=True)

    value = Column(Text)

    categories = relationship('Category', back_populates="direct")
