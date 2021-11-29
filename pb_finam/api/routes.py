from fastapi import APIRouter
from tags_agr.api.local_routes import api

routes = APIRouter()

routes.include_router(api.router, prefix='/api')
