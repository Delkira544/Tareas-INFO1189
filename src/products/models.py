from dataclasses import dataclass
from typing import Optional

@dataclass
class Category:
    id: int
    name: str
    description: str | None = None

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
        }

@dataclass
class Product:
    id: int
    name: str
    price: float
    in_stock: bool
    currency: str = "CLP"
    category_id: int | None = None
    category_name: str | None = None

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "in_stock": self.in_stock,
            "currency": self.currency,
            "category_id": self.category_id,
            "category_name": self.category_name,
        }

@dataclass
class ProductRequest:
    name: str
    price: float
    in_stock: bool
    currency: str = "CLP"
    category_id: int | None = None

    def to_dict(self):
        return {
            "name": self.name,
            "price": self.price,
            "in_stock": self.in_stock,
            "currency": self.currency,
            "category_id": self.category_id,
        }

@dataclass
class ProductUpdate:
    name: str | None = None
    price: float | None = None
    in_stock: bool | None = None
    currency: str | None = None
    category_id: int | None = None

    def to_dict(self):
        return {
            "name": self.name,
            "price": self.price,
            "in_stock": self.in_stock,
            "currency": self.currency,
            "category_id": self.category_id,
        }

@dataclass
class CategoryRequest:
    name: str
    description: str | None = None

    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
        }
