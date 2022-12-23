import logging
from sqlalchemy.orm import Session

from app import repositories as repo
from app.schemas.user import UserCreate
from app.schemas.recipe import RecipeCreate
from app.db import base  # noqa: F401
from .recipe_data import RECIPES

logger = logging.getLogger(__name__)

FIRST_SUPERUSER = "admin@recipeapi.com"

# make sure all SQL Alchemy models are imported (app.db.base) before initializing DB
# otherwise, SQL Alchemy might fail to initialize relationships properly
# for more details: https://github.com/tiangolo/full-stack-fastapi-postgresql/issues/28


def init_db(db: Session) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next line
    # Base.metadata.create_all(bind=engine)
    if FIRST_SUPERUSER:
        user = repo.user.get_by_email(db, email=FIRST_SUPERUSER)
        if not user:
            user_in = UserCreate(
                first_name="Super User",
                email=FIRST_SUPERUSER,
                password='password',
                is_superuser=True,
            )
            user = repo.user.create(db, obj_in=user_in)  # noqa: F841
        else:
            logger.warning(
                "Skipping creating superuser. User with email "
                f"{FIRST_SUPERUSER} already exists. "
            )
        if not user.recipes:
            for recipe in RECIPES:
                recipe_in = RecipeCreate(
                    label=recipe["label"],
                    source=recipe["source"],
                    url=recipe["url"],
                    submitter_id=user.id,
                )
                repo.recipe.create(db, obj_in=recipe_in)
    else:
        logger.warning(
            "Skipping creating superuser.  FIRST_SUPERUSER needs to be "
            "provided as an env variable. "
            "e.g.  FIRST_SUPERUSER=admin@api.coursemaker.io"
        )