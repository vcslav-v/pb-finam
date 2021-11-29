APP_NAME = pb_finam
APP_AUTHOR = vaclav-v

FILE_VSCODE_SETTINGS = .vscode/settings.json
FILE_LINT_SETTINGS = setup.cfg

define VSCODE_SETTINGS
echo "{" >> $(FILE_VSCODE_SETTINGS)
echo "\"python.pythonPath\": \"`poetry show -v 2 | grep virtualenv | cut -d ' ' -f 3 | xargs` \"," >> $(FILE_VSCODE_SETTINGS)
echo "\"python.linting.pylintEnabled\": false," >> $(FILE_VSCODE_SETTINGS)
echo "\"python.linting.flake8Enabled\": true," >> $(FILE_VSCODE_SETTINGS)
echo "\"python.linting.mypyEnabled\": true," >> $(FILE_VSCODE_SETTINGS)
echo "\"python.linting.enabled\": true," >> $(FILE_VSCODE_SETTINGS)
echo "}" >> $(FILE_VSCODE_SETTINGS)

endef


FILE_GITIGNORE = .gitignore

define GITIGNORE
echo ".venv" >> $(FILE_GITIGNORE)
echo ".vscode" >> $(FILE_GITIGNORE)
echo "*_cache" >> $(FILE_GITIGNORE)
echo "__pycache__" >> $(FILE_GITIGNORE)
echo ".python-version" >> $(FILE_GITIGNORE)
echo "${FILE_LINT_SETTINGS}" >> $(FILE_GITIGNORE)

endef

define FASTAPI_ROUTES
echo "from fastapi import APIRouter" >> $(APP_NAME)/api/routes.py
echo "from $(APP_NAME).api.local_routes import api" >> $(APP_NAME)/api/routes.py
echo "" >> $(APP_NAME)/api/routes.py
echo "routes = APIRouter()" >> $(APP_NAME)/api/routes.py
echo "" >> $(APP_NAME)/api/routes.py
echo "routes.include_router(api.router, prefix='/api')" >> $(APP_NAME)/api/routes.py

endef

define FASTAPI_API
echo "import os" >> $(APP_NAME)/api/local_routes/api.py
echo "import secrets" >> $(APP_NAME)/api/local_routes/api.py
echo "" >> $(APP_NAME)/api/local_routes/api.py
echo "from fastapi import APIRouter, Depends, HTTPException, status" >> $(APP_NAME)/api/local_routes/api.py
echo "from fastapi.security import HTTPBasic, HTTPBasicCredentials" >> $(APP_NAME)/api/local_routes/api.py
echo "" >> $(APP_NAME)/api/local_routes/api.py
echo "router = APIRouter()" >> $(APP_NAME)/api/local_routes/api.py
echo "security = HTTPBasic()" >> $(APP_NAME)/api/local_routes/api.py
echo "" >> $(APP_NAME)/api/local_routes/api.py
echo "username = os.environ.get('API_USERNAME') or 'root'" >> $(APP_NAME)/api/local_routes/api.py
echo "password = os.environ.get('API_PASSWORD') or 'pass'" >> $(APP_NAME)/api/local_routes/api.py
echo "" >> $(APP_NAME)/api/local_routes/api.py
echo "" >> $(APP_NAME)/api/local_routes/api.py
echo "def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):" >> $(APP_NAME)/api/local_routes/api.py
echo "    correct_username = secrets.compare_digest(credentials.username, username)" >> $(APP_NAME)/api/local_routes/api.py
echo "    correct_password = secrets.compare_digest(credentials.password, password)" >> $(APP_NAME)/api/local_routes/api.py
echo "    if not (correct_username and correct_password):" >> $(APP_NAME)/api/local_routes/api.py
echo "        raise HTTPException(" >> $(APP_NAME)/api/local_routes/api.py
echo "            status_code=status.HTTP_401_UNAUTHORIZED," >> $(APP_NAME)/api/local_routes/api.py
echo "            detail="Incorrect username or password"," >> $(APP_NAME)/api/local_routes/api.py
echo "            headers={"WWW-Authenticate": "Basic"}," >> $(APP_NAME)/api/local_routes/api.py
echo "        )" >> $(APP_NAME)/api/local_routes/api.py
echo "    return credentials.username" >> $(APP_NAME)/api/local_routes/api.py
echo "" >> $(APP_NAME)/api/local_routes/api.py
echo "" >> $(APP_NAME)/api/local_routes/api.py
echo "@router.get('/test')" >> $(APP_NAME)/api/local_routes/api.py
echo "def test( _: str = Depends(get_current_username)):" >> $(APP_NAME)/api/local_routes/api.py
echo "     pass >> $(APP_NAME)/api/local_routes/api.py

echo "from fastapi import FastAPI" >> $(APP_NAME)/main.py
echo "from $(APP_NAME).api.routes import routes" >> $(APP_NAME)/main.py
echo "" >> $(APP_NAME)/main.py
echo "app = FastAPI(debug=True)" >> $(APP_NAME)/main.py
echo "" >> $(APP_NAME)/main.py
echo "app.include_router(routes)" >> $(APP_NAME)/main.py


endef

define DBPY
echo "from sqlalchemy import create_engine" >> $(APP_NAME)/db.py
echo "from sqlalchemy.orm import sessionmaker" >> $(APP_NAME)/db.py
echo "from os import environ" >> $(APP_NAME)/db.py
echo "" >> $(APP_NAME)/db.py
echo "if environ.get('DATABASE_URL'):" >> $(APP_NAME)/db.py
echo "    SQLALCHEMY_DATABASE_URI = environ.get('DATABASE_URL').replace(" >> $(APP_NAME)/db.py
echo "        'postgres', 'postgresql+psycopg2'" >> $(APP_NAME)/db.py
echo "    )" >> $(APP_NAME)/db.py
echo "else:" >> $(APP_NAME)/db.py
echo "    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://postgres:mysecretpassword@0.0.0.0/postgres'" >> $(APP_NAME)/db.py
echo "" >> $(APP_NAME)/db.py
echo "engine = create_engine(SQLALCHEMY_DATABASE_URI)" >> $(APP_NAME)/db.py
echo "SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)" >> $(APP_NAME)/db.py

echo "from sqlalchemy import Column, Integer" >> $(APP_NAME)/models.py
echo "from sqlalchemy.ext.declarative import declarative_base" >> $(APP_NAME)/models.py
echo "" >> $(APP_NAME)/models.py
echo "Base = declarative_base()" >> $(APP_NAME)/models.py
echo "" >> $(APP_NAME)/models.py
echo "" >> $(APP_NAME)/models.py
echo "class Item(Base):" >> $(APP_NAME)/models.py
echo "    '''Items.'''" >> $(APP_NAME)/models.py
echo "" >> $(APP_NAME)/models.py
echo "    __tablename__ = 'items'" >> $(APP_NAME)/models.py
echo "" >> $(APP_NAME)/models.py
echo "    id = Column(Integer, primary_key=True)" >> $(APP_NAME)/models.py

endef

define FLAKE8_SETTINGS
echo "[flake8]" >> $(FILE_LINT_SETTINGS)
echo "    max-line-length = 100" >> $(FILE_LINT_SETTINGS)

endef

define MYPY_SETTINGS
echo "    # alembic" >> $(FILE_LINT_SETTINGS)
echo "    exclude = alembic/*" >> $(FILE_LINT_SETTINGS)
echo "[mypy]" >> $(FILE_LINT_SETTINGS)
echo "    plugins = sqlmypy" >> $(FILE_LINT_SETTINGS)

endef


init:
	poetry init -n --name $(APP_NAME) --author $(APP_AUTHOR)
	poetry add --dev flake8
	poetry add --dev mypy
	poetry add loguru
	mkdir .vscode
	touch $(FILE_VSCODE_SETTINGS)
	$(VSCODE_SETTINGS)
	touch $(FILE_GITIGNORE)
	$(GITIGNORE)
	touch $(FILE_LINT_SETTINGS)
	$(FLAKE8_SETTINGS)
	mkdir $(APP_NAME)
	touch $(APP_NAME)/__init__.py
	echo '"""Main module $(APP_NAME) project."""' > $(APP_NAME)/__init__.py
	poetry shell

fastapi:
	poetry add fastapi
	poetry add gunicorn
	poetry add uvicorn
	poetry add python-multipart
	poetry add pydantic
	touch $(APP_NAME)/main.py
	mkdir $(APP_NAME)/api
	touch $(APP_NAME)/api/__init__.py
	touch $(APP_NAME)/api/routes.py
	touch $(APP_NAME)/api/service.py
	$(FASTAPI_ROUTES)
	mkdir $(APP_NAME)/api/local_routes
	touch $(APP_NAME)/api/local_routes/__init__.py
	touch $(APP_NAME)/api/local_routes/api.py
	$(FASTAPI_API)



lint:
	poetry run flake8 $(APP_NAME)
	poetry run mypy $(APP_NAME)

install:
	poetry install

sqlalchemy:
	poetry add sqlalchemy
	poetry add psycopg2-binary
	poetry add alembic
	poetry run alembic init alembic
	$(MYPY_SETTINGS)
	touch $(APP_NAME)/models.py
	touch $(APP_NAME)/db.py
	$(DBPY)



db_revision:
	poetry run alembic revision --autogenerate

db_update:
	poetry run alembic upgrade head

test_db:
	docker run --name test-postgres -e POSTGRES_PASSWORD=mysecretpassword -e POSTGRES_DB=postgres -d -p 5432:5432 postgres

req:
	poetry export -f requirements.txt --output requirements.txt --without-hashes