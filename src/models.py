from dataclasses import dataclass

@dataclass
class Product:
    id: int
    name: str
    price: float
    in_stock: bool
    currency: str = "CLP"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "in_stock": self.in_stock,
            "currency": self.currency,
        }

@dataclass
class ProductRequest:
    name: str
    price: float
    in_stock: bool
    currency: str = "CLP"

    def to_dict(self):
        return {
            "name": self.name,
            "price": self.price,
            "in_stock": self.in_stock,
            "currency": self.currency,
        }

@dataclass
class ProductUpdate:
    name: str | None = None
    price: float | None = None
    in_stock: bool | None = None
    currency: str | None = None

    def to_dict(self):
        return {
            "name": self.name,
            "price": self.price,
            "in_stock": self.in_stock,
            "currency": self.currency,
        }
