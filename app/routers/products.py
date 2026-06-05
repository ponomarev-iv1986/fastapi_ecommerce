from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import and_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.db_depends import get_async_db, get_db
from app.models.categories import Category as CategoryModel
from app.models.products import Product as ProductModel
from app.schemas import Product as ProductSchema
from app.schemas import ProductCreate

# Создаём маршрутизатор для товаров
router = APIRouter(
    prefix="/products",
    tags=["products"],
)


@router.get("/", response_model=list[ProductSchema], status_code=status.HTTP_200_OK)
async def get_all_products(db: AsyncSession = Depends(get_async_db)):
    """
    Возвращает список всех товаров.
    """
    stmt = select(ProductModel).where(ProductModel.is_active == True).order_by(ProductModel.id)
    result = await db.scalars(stmt)
    products = result.all()

    return products


@router.post("/", response_model=ProductSchema, status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductCreate, db: AsyncSession = Depends(get_async_db)):
    """
    Создаёт новый товар.
    """
    # Проверка существования активной категории
    stmt = select(CategoryModel).where(and_(CategoryModel.id == product.category_id, CategoryModel.is_active == True))
    result = await db.scalars(stmt)
    category = result.first()
    if category is None:
        raise HTTPException(status_code=400, detail="Category not found or inactive")

    # Создание продукта
    db_product = ProductModel(**product.model_dump())
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)

    return db_product


@router.get("/category/{category_id}", response_model=list[ProductSchema], status_code=status.HTTP_200_OK)
async def get_products_by_category(category_id: int, db: AsyncSession = Depends(get_async_db)):
    """
    Возвращает список товаров в указанной категории по её ID.
    """
    # Проверка существования категории
    stmt = select(CategoryModel).where(and_(CategoryModel.id == category_id, CategoryModel.is_active == True))
    result_category = await db.scalars(stmt)
    category = result_category.first()
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found or inactive")

    # Получение продуктов по категории
    category_products_stmt = select(ProductModel).where(
        and_(ProductModel.category_id == category_id, ProductModel.is_active == True)
    )
    result_category_products = await db.scalars(category_products_stmt)
    category_products = result_category_products.all()

    return category_products


@router.get("/{product_id}", response_model=ProductSchema, status_code=status.HTTP_200_OK)
async def get_product(product_id: int, db: AsyncSession = Depends(get_async_db)):
    """
    Возвращает детальную информацию о товаре по его ID.
    """
    stmt = select(ProductModel).where(and_(ProductModel.id == product_id, ProductModel.is_active == True))
    result_product = await db.scalars(stmt)
    product: ProductModel | None = result_product.first()

    # Проверка существования товара
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found or inactive")

    # Проверка существования категории
    category_stmt = select(CategoryModel).where(
        and_(CategoryModel.id == product.category_id, CategoryModel.is_active == True)
    )
    result_category = await db.scalars(category_stmt)
    category = result_category.first()
    if category is None:
        raise HTTPException(status_code=400, detail="Category not found or inactive")

    return product


@router.put("/{product_id}", response_model=ProductSchema, status_code=status.HTTP_200_OK)
async def update_product(product_id: int, product: ProductCreate, db: AsyncSession = Depends(get_async_db)):
    """
    Обновляет товар по его ID.
    """
    # Проверка существования активного товара
    stmt = select(ProductModel).where(and_(ProductModel.id == product_id, ProductModel.is_active == True))
    result_db_product = await db.scalars(stmt)
    db_product = result_db_product.first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found or inactive")

    # Проверка существования категории
    category_stmt = select(CategoryModel).where(
        and_(CategoryModel.id == product.category_id, CategoryModel.is_active == True)
    )
    result_category = await db.scalars(category_stmt)
    category = result_category.first()
    if category is None:
        raise HTTPException(status_code=400, detail="Category not found or inactive")

    # Обновление товара
    await db.execute(update(ProductModel).where(ProductModel.id == product_id).values(**product.model_dump()))
    await db.commit()
    await db.refresh(db_product)

    return db_product


@router.delete("/{product_id}", response_model=ProductSchema, status_code=status.HTTP_200_OK)
async def delete_product(product_id: int, db: AsyncSession = Depends(get_async_db)):
    """
    Удаляет товар по его ID.
    """
    # Проверка существования активного товара
    stmt = select(ProductModel).where(and_(ProductModel.id == product_id, ProductModel.is_active == True))
    result = await db.scalars(stmt)
    product = result.first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found or inactive")

    # Логическое удаление товара, установка is_active == True
    await db.execute(update(ProductModel).where(ProductModel.id == product_id).values(is_active=False))
    await db.commit()
    await db.refresh(product)

    return product
