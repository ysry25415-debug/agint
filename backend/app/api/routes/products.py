"""
Products API endpoints.
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List, Optional
from datetime import datetime
from sqlmodel import Session, select

from ...models.base import Product, ProductCategory
from ...schemas.base import ProductOut, ProductDetailOut, APIResponse
from ...core.database import get_db

router = APIRouter(tags=["Products"])


@router.get("/products", response_model=APIResponse)
async def list_products(
    category: Optional[ProductCategory] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    min_score: float = Query(0.0, ge=0, le=100),
    db: Session = Depends(get_db),
):
    """
    List products with filtering and pagination.
    """
    query = select(Product)

    if category:
        query = query.where(Product.category == category.value)

    query = query.offset(offset).limit(limit)

    products = db.exec(query).all()

    return APIResponse(
        success=True,
        message=f"Retrieved {len(products)} products",
        data=products,
    )


@router.get("/products/{product_id}", response_model=APIResponse)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    """Get a specific product by ID."""
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return APIResponse(
        success=True,
        message="Product retrieved",
        data=product,
    )


@router.get("/products/search", response_model=APIResponse)
async def search_products(
    q: str = Query(..., min_length=2),
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """Search products by name."""
    query = select(Product).where(
        Product.normalized_name.ilike(f"%{q}%")
    )

    products = db.exec(query.limit(limit)).all()

    return APIResponse(
        success=True,
        message=f"Found {len(products)} products matching '{q}'",
        data=products,
    )