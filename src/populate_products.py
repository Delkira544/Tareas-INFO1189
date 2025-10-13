"""
Populate Products Script
Script para poblar la base de datos con datos de ejemplo
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from infrastructure.container import container


def populate_sample_data():
    """Poblar base de datos con productos de ejemplo"""
    
    print("🔄 Poblando base de datos con datos de ejemplo...")
    
    # Obtener casos de uso
    product_uc = container.get_product_use_cases()
    category_uc = container.get_category_use_cases()
    subcategory_uc = container.get_subcategory_use_cases()
    
    try:
        # Obtener categorías y subcategorías existentes
        categories = category_uc.get_all_categories()
        subcategories = subcategory_uc.get_all_subcategories()
        
        if not categories or not subcategories:
            print("❌ No se encontraron categorías o subcategorías. Verifica la inicialización de la BD.")
            return
        
        # Productos de ejemplo por subcategoría
        sample_products = [
            # Micrófonos (subcategory_id: 1)
            ("Blue Yeti USB", 150000, 1, "CLP"),
            ("Audio-Technica AT2020", 180000, 1, "CLP"),
            ("Shure SM7B", 450000, 1, "CLP"),
            
            # Cámaras Web (subcategory_id: 2)
            ("Logitech C920", 95000, 2, "CLP"),
            ("Razer Kiyo", 120000, 2, "CLP"),
            ("Elgato Facecam", 200000, 2, "CLP"),
            
            # Auriculares (subcategory_id: 3)
            ("Sony WH-1000XM4", 280000, 3, "CLP"),
            ("SteelSeries Arctis 7", 150000, 3, "CLP"),
            ("Audio-Technica ATH-M50x", 120000, 3, "CLP"),
            
            # Tarjetas de Video (subcategory_id: 4)
            ("NVIDIA RTX 4090", 2500000, 4, "CLP"),
            ("AMD RX 7800 XT", 800000, 4, "CLP"),
            ("NVIDIA RTX 4070", 650000, 4, "CLP"),
            
            # Procesadores (subcategory_id: 5)
            ("Intel i9-13900K", 650000, 5, "CLP"),
            ("AMD Ryzen 9 7900X", 580000, 5, "CLP"),
            ("Intel i5-13600K", 380000, 5, "CLP"),
            
            # Memorias RAM (subcategory_id: 6)
            ("Corsair Vengeance 32GB DDR5", 250000, 6, "CLP"),
            ("G.Skill Trident Z5 16GB", 150000, 6, "CLP"),
            ("Kingston Fury 64GB DDR5", 450000, 6, "CLP"),
            
            # SSD (subcategory_id: 9)
            ("Samsung 980 PRO 1TB", 120000, 9, "CLP"),
            ("WD Black SN850X 2TB", 280000, 9, "CLP"),
            ("Crucial MX4 500GB", 65000, 9, "CLP"),
            
            # Teclados (subcategory_id: 12)
            ("Corsair K95 RGB Platinum", 180000, 12, "CLP"),
            ("Razer BlackWidow V3", 120000, 12, "CLP"),
            ("Logitech MX Keys", 95000, 12, "CLP"),
            
            # Mouse (subcategory_id: 13)
            ("Logitech G Pro X Superlight", 85000, 13, "CLP"),
            ("Razer DeathAdder V3", 65000, 13, "CLP"),
            ("SteelSeries Rival 650", 75000, 13, "CLP"),
            
            # Monitores Gaming (subcategory_id: 15)
            ("ASUS ROG Swift PG279QM", 850000, 15, "CLP"),
            ("Samsung Odyssey G7", 550000, 15, "CLP"),
            ("LG UltraGear 27GP850", 380000, 15, "CLP"),
        ]
        
        created_count = 0
        
        for name, price, subcategory_id, currency in sample_products:
            try:
                product = product_uc.create_product(
                    name=name,
                    price=price,
                    subcategory_id=subcategory_id,
                    in_stock=True,
                    currency=currency
                )
                created_count += 1
                print(f"✅ Creado: {product.name} - ${product.price:,} {product.currency}")
                
            except Exception as e:
                print(f"❌ Error creando {name}: {str(e)}")
        
        print(f"\n🎉 Proceso completado!")
        print(f"📦 {created_count} productos creados exitosamente")
        print(f"🏷️  {len(categories)} categorías disponibles")
        print(f"🔖 {len(subcategories)} subcategorías disponibles")
        
        # Mostrar resumen por categoría
        print("\n📊 Resumen por categoría:")
        for category in categories:
            products_in_category = product_uc.get_products_by_category(category.id)
            print(f"   {category.name}: {len(products_in_category)} productos")
    
    except Exception as e:
        print(f"❌ Error general: {str(e)}")


if __name__ == "__main__":
    populate_sample_data()
