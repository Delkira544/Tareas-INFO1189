from src.products.models import ProductRequest
from src.products.repository import ProductRepository

# Crear repositorio
repo = ProductRepository()

# Crear producto de prueba
product_request = ProductRequest(
    name="Laptop",
    price=999.99,
    in_stock=True,
    currency="USD"
)

# Guardar en base de datos
product = repo.create(product_request)
print(f"Producto creado: {product.to_dict()}")

# Obtener todos los productos
products = repo.get_all()
print(f"Total productos: {len(products)}")
for p in products:
    print(f"- {p.name}: ${p.price}")