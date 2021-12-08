from __future__ import annotations
from pydantic import BaseModel
from datetime import date as date_type
from typing import Optional


class Node(BaseModel):
    id: Optional[int]
    name: str
    children: list[Node] = []


Node.update_forward_refs()


class Settings(BaseModel):
    """DB settings"""
    currencies: list[str]
    categories: list[Node]


class Transaction(BaseModel):
    id: Optional[int]
    date: date_type
    value: int
    comment: str
    currency_id: int
    category_id: int
    category_id_path: Optional[list[int]]


class PageTransaction(BaseModel):
    id: int
    date: str
    value: str
    comment: str
    base_category: str
    category: str


class TransactionPage(BaseModel):
    rows: list[PageTransaction] = []


class GetTransactionPage(BaseModel):
    from_date: date_type
    page: Optional[int]


class ShortStat(BaseModel):
    frm: date_type
    to: date_type
    income: Optional[int]
    expense: Optional[int]
    profit: Optional[int]


class Item(BaseModel):
    id: int
    name: str


class Items(BaseModel):
    items: list[Item] = []


class Debt(BaseModel):
    name: str
    value: int


class Acc(BaseModel):
    name: str
    debt: list[Debt]


class Debts(BaseModel):
    accs: list[Acc]
