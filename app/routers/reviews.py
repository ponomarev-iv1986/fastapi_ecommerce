from fastapi import APIRouter, HTTPException, status
from fastapi.params import Depends
from sqlalchemy import and_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

from app.auth import get_current_buyer, get_current_user
from app.db_depends import get_async_db
from app.models.products import Product as ProductModel
from app.models.reviews import Review as ReviewModel
from app.schemas import Review as ReviewSchema
from app.schemas import ReviewCreate
from app.schemas import User as UserModel

router = APIRouter(
    prefix="/reviews",
    tags=["reviews"],
)


async def update_product_rating(db: AsyncSession, product_id: int):
    result = await db.execute(
        select(func.avg(ReviewModel.grade)).where(ReviewModel.product_id == product_id, ReviewModel.is_active == True)
    )
    avg_rating = result.scalar() or 0.0
    product = await db.get(ProductModel, product_id)
    product.rating = avg_rating
    await db.commit()


@router.get("/", response_model=list[ReviewSchema], status_code=status.HTTP_200_OK)
async def get_all_reviews(db: AsyncSession = Depends(get_async_db)):
    """
    Возвращает список всех отзывов.
    """
    stmt = select(ReviewModel).where(ReviewModel.is_active == True).order_by(ReviewModel.id)
    reviews_scalar = await db.scalars(stmt)
    review_result = reviews_scalar.all()

    return review_result


@router.post("/", response_model=ReviewSchema, status_code=status.HTTP_201_CREATED)
async def create_review(
    review: ReviewCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_current_buyer),
):
    """
    Создает новый отзыв для товара, привязанный к текущему покупателю (только для "buyer").
    """
    # Проверка существования продукта
    product_stmt = select(ProductModel).where(
        and_(ProductModel.id == review.product_id, ProductModel.is_active == True)
    )
    product_scalar = await db.scalars(product_stmt)
    product_result = product_scalar.first()
    if not product_result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found or inactive")

    # Проверка существования отзыва о продукте от текущего пользователя
    review_stmt = select(ReviewModel).where(
        and_(
            ReviewModel.product_id == review.product_id,
            ReviewModel.user_id == current_user.id,
            ReviewModel.is_active == True,
        )
    )
    review_scalar = await db.scalars(review_stmt)
    review_result = review_scalar.first()
    if review_result:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Review from user already exists")

    # Добавляем отзыв в БД
    db_review = ReviewModel(**review.model_dump(), user_id=current_user.id)
    db.add(db_review)
    await update_product_rating(db, review.product_id)
    await db.commit()
    await db.refresh(db_review)

    return db_review


@router.delete("/reviews/{review_id}", response_model=ReviewSchema, status_code=status.HTTP_200_OK)
async def delete_review(
    review_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_current_user),
):
    """
    Выполняет мягкое удаление отзыва, если он принадлежит текущему пользователю, или админу.
    """
    # Проверка существования отзыва
    review_stmt = select(ReviewModel).where(and_(ReviewModel.id == review_id, ReviewModel.is_active == True))
    review_scalar = await db.scalars(review_stmt)
    review_result = review_scalar.first()
    if not review_result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found or inactive")

    # Проверка пользователя
    if not (current_user.role == "admin" or current_user.id == review_result.user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Only admin or review author can perform this action"
        )

    # Мягкое удаление отзыва
    stmt = update(ReviewModel).where(ReviewModel.id == review_id).values(is_active=False)
    await db.execute(stmt)
    await update_product_rating(db, review_result.product_id)
    await db.commit()
    await db.refresh(review_result)

    return review_result
