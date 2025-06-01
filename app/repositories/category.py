from app.models import Category
from app.repositories.base import RepositoryFactory


class CategoryRepository(RepositoryFactory(Category)):
    pass
