import os
import secrets

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pb_finam import schemas, db_tools
from loguru import logger

router = APIRouter()
security = HTTPBasic()

username = os.environ.get('API_USERNAME') or 'api'
password = os.environ.get('API_PASSWORD') or 'pass'


def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, username)
    correct_password = secrets.compare_digest(credentials.password, password)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Basic'},
        )
    return credentials.username


@router.post('/set_db')
def set_db(settings: schemas.Settings, _: str = Depends(get_current_username)):
    logger.warning('DB setup')
    db_tools.setup(settings)


@router.post('/transaction')
def set_transaction(transaction: schemas.Transaction, _: str = Depends(get_current_username)):
    logger.info(transaction)
    db_tools.add_transaction(transaction)


@router.get('/transaction')
def get_transaction(trans_id: int, _: str = Depends(get_current_username)):
    return db_tools.get_transaction(trans_id)


@router.post('/rm_transaction')
def rm_transaction(trans_id: int, _: str = Depends(get_current_username)):
    db_tools.rm_transaction(trans_id)


@router.get('/transactions')
def get_transactions(page_data: schemas.GetTransactionPage, _: str = Depends(get_current_username)):
    return db_tools.get_transactions(page_data)


@router.get('/short-stat')
def get_short_stat(_: str = Depends(get_current_username)):
    return db_tools.get_short_stat()


@router.get('/category-tree')
def get_category_tree(
    _: str = Depends(get_current_username)
) -> schemas.Node:
    return db_tools.get_category_tree()


@router.get('/сurrencies')
def get_сurrencies(_: str = Depends(get_current_username)) -> schemas.Items:
    return db_tools.get_сurrencies()


@router.get('/debt')
def get_debt(_: str = Depends(get_current_username)) -> schemas.Debts:
    return db_tools.get_debt()
