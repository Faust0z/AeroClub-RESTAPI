from fastapi import Depends
from sqlalchemy.orm import Session

from .database import get_db

get_db_dependency = Depends(get_db)