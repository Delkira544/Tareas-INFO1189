"""
Script para poblar la base de datos con productos de ejemplo
3 productos por cada categoría, todos en pesos chilenos (CLP)

Ejecutar desde la carpeta src:
    python populate_products.py
"""
from products.repository import ProductRepository, CategoryRepository
from products.models import ProductRequest


def populate_products():
    product_repo = ProductRepository()
    category_repo = CategoryRepository()
    
    # Obtener todas las categorías
    categories = category_repo.get_all()
    print(f"📦 Encontradas {len(categories)} categorías")
    print()
    
    # Productos por categoría (3 cada una)
    products_data = {
        "Micrófonos": [
            {"name": "HyperX QuadCast", "price": 89990, "in_stock": True},
            {"name": "Blue Yeti USB", "price": 129990, "in_stock": True},
            {"name": "Razer Seiren Mini", "price": 49990, "in_stock": False},
        ],
        "Tarjetas de Video": [
            {"name": "NVIDIA RTX 4090 24GB", "price": 2499990, "in_stock": True},
            {"name": "AMD RX 7900 XTX 24GB", "price": 1599990, "in_stock": True},
            {"name": "NVIDIA RTX 4070 Ti 12GB", "price": 1199990, "in_stock": False},
        ],
        "Memorias RAM": [
            {"name": "Kingston Fury 16GB DDR4 3200MHz", "price": 45990, "in_stock": True},
            {"name": "Corsair Vengeance 32GB DDR5 5600MHz", "price": 159990, "in_stock": True},
            {"name": "G.Skill Trident Z5 64GB DDR5 6000MHz", "price": 349990, "in_stock": True},
        ],
        "Placas Madres": [
            {"name": "ASUS ROG Strix Z790-E Gaming", "price": 599990, "in_stock": True},
            {"name": "MSI MAG B650 TOMAHAWK WiFi", "price": 249990, "in_stock": True},
            {"name": "Gigabyte X670 AORUS Elite AX", "price": 429990, "in_stock": False},
        ],
        "Discos Duros": [
            {"name": "Samsung 990 PRO SSD 2TB NVMe", "price": 179990, "in_stock": True},
            {"name": "WD Black SN850X 1TB NVMe", "price": 129990, "in_stock": True},
            {"name": "Seagate Barracuda HDD 4TB", "price": 89990, "in_stock": True},
        ],
        "Fuentes de Poder": [
            {"name": "Corsair RM1000e 1000W 80+ Gold", "price": 199990, "in_stock": True},
            {"name": "EVGA SuperNOVA 850W 80+ Platinum", "price": 169990, "in_stock": True},
            {"name": "Seasonic Focus GX-750 750W 80+ Gold", "price": 129990, "in_stock": False},
        ],
    }
    
    # Crear productos
    total_created = 0
    for category in categories:
        category_name = category.name
        if category_name in products_data:
            print(f"🏷️  Categoría: {category_name} (ID: {category.id})")
            
            for product_data in products_data[category_name]:
                product_request = ProductRequest(
                    name=product_data["name"],
                    price=product_data["price"],
                    in_stock=product_data["in_stock"],
                    currency="CLP",
                    category_id=category.id
                )
                
                try:
                    product = product_repo.create(product_request)
                    status = "✅ Disponible" if product.in_stock else "❌ Agotado"
                    print(f"   ✓ {product.name} - ${product.price:,} CLP {status}")
                    total_created += 1
                except Exception as e:
                    print(f"   ✗ Error al crear {product_data['name']}: {e}")
            
            print()
    
    print(f"🎉 Total de productos creados: {total_created}/18")
    print()
    
    # Mostrar resumen
    print("📊 Resumen por categoría:")
    for category in categories:
        products = product_repo.get_by_category(category.id)
        available = sum(1 for p in products if p.in_stock)
        print(f"   • {category.name}: {len(products)} productos ({available} disponibles)")


if __name__ == "__main__":
    print("=" * 70)
    print("🛒 POBLANDO BASE DE DATOS - TIENDA DE INFORMÁTICA")
    print("=" * 70)
    print()
    
    try:
        populate_products()
        print()
        print("=" * 70)
        print("✅ Base de datos poblada exitosamente")
        print("=" * 70)
    except Exception as e:
        print()
        print("=" * 70)
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        print("=" * 70)
