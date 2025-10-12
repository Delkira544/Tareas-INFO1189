API Tienda de Informática

Descripción

API REST y GraphQL para gestionar productos y categorías de una tienda de informática. Implementada en Python con FastAPI y Strawberry GraphQL.

Requisitos

- Python 3.12+
- Dependencias en `requirements.txt`

Instalación

1. Crear y activar un entorno virtual (recomendado):

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Instalar dependencias:

```bash
pip install -r requirements.txt
```

Ejecución

```bash
cd src
uvicorn main:app --reload
```

El servidor queda disponible en `http://localhost:8000`.

Archivos importantes

- `src/main.py` - Punto de entrada
- `src/presentation/api/` - Rutas REST y GraphQL
- `src/infrastructure/database.py` - Inicialización de la base de datos SQLite
- `src/infrastructure/repositories.py` - Acceso a datos
- `src/application/use_cases.py` - Lógica de aplicación
- `src/domain/` - Entidades e interfaces
- `populate_products.py` - Script para poblar la base de datos con ejemplos

Autenticación

Para los endpoints protegidos se usa un header `Authorization: Bearer secreto123`.

Endpoints principales (REST)

Productos

- `GET /products` — Listar productos
- `GET /products/{id}` — Obtener producto por id
- `POST /products` — Crear producto (requiere token)
- `PUT /products/{id}` — Actualizar producto
- `PATCH /products/{id}` — Actualizar parcialmente
- `DELETE /products/{id}` — Eliminar producto

Categorías

- `GET /categories` — Listar categorías
- `GET /categories/{id}` — Obtener categoría por id
- `GET /categories/{id}/products` — Productos de una categoría
- `POST /categories` — Crear categoría
- `DELETE /categories/{id}` — Eliminar categoría

GraphQL

- GraphQL disponible en `POST /graphql` (playground en el navegador cuando está habilitado)
- Queries principales: `categories`, `category(id)`, `products(categoryId?)`, `product(id)`
- Mutations principales: `createProduct`, `updateProduct`, `deleteProduct`, `createCategory`, `deleteCategory`

Notas

- La base de datos SQLite se crea en `src/data/` al iniciar la aplicación si no existe.
- El script `populate_products.py` inserta datos de ejemplo (18 productos, 6 categorías).

Contacto

Si necesitas que deje solo los archivos mínimos para entregar, o que archive los archivos antiguos, dime y lo hago.

#### Eliminar producto
```bash
curl -X DELETE http://localhost:8000/products/1
```

### API GraphQL

Acceder a GraphQL Playground: `http://localhost:8000/graphql`

#### Query: Obtener todas las categorías
```graphql
query {
  categories {
    id
    name
    description
  }
}
```

#### Query: Obtener todos los productos con categoría
```graphql
query {
  products {
    id
    name
    price
    inStock
    currency
    categoryId
    categoryName
  }
}
```

#### Query: Obtener productos filtrados por categoría
```graphql
query {
  products(categoryId: 2) {
    id
    name
    price
    categoryName
  }
}
```

#### Query: Obtener producto por ID
```graphql
query {
  product(productId: 1) {
    id
    name
    price
    inStock
    currency
    categoryName
  }
}
```

#### Mutation: Crear categoría
```graphql
mutation {
  createCategory(input: {
    name: "Procesadores"
    description: "CPUs Intel y AMD"
  }) {
    id
    name
    description
  }
}
```

#### Mutation: Crear producto con categoría
```graphql
mutation {
  createProduct(input: {
    name: "RTX 4090"
    price: 1999.99
    inStock: true
    currency: "USD"
    categoryId: 2
  }) {
    id
    name
    price
    inStock
    currency
    categoryName
  }
}
```

#### Mutation: Actualizar producto
```graphql
mutation {
  updateProduct(productId: 1, input: {
    price: 899.99
    categoryId: 3
  }) {
    id
    name
    price
    inStock
    currency
    categoryName
  }
}
```

#### Mutation: Eliminar producto
```graphql
mutation {
  deleteProduct(productId: 1)
}
```

#### Mutation: Eliminar categoría
```graphql
mutation {
  deleteCategory(categoryId: 1)
}
```

## 📁 Estructura del Proyecto

```
src/
├── main.py                  # Aplicación FastAPI principal
├── config/
│   ├── __init__.py
│   ├── config.py           # Configuración general
│   └── database.py         # Gestión de base de datos SQLite
├── products/
│   ├── __init__.py
│   ├── controller.py       # Lógica de negocio
│   ├── models.py           # Modelos de datos (Product, Category)
│   ├── repository.py       # Acceso a datos
│   └── routes.py           # Endpoints REST de productos
├── categories/
│   ├── __init__.py
│   └── routes.py           # Endpoints REST de categorías
├── graphql_api/
│   ├── __init__.py
│   ├── schema.py           # Schema GraphQL
│   ├── resolvers.py        # Resolvers (Query y Mutation)
│   └── types.py            # Tipos GraphQL
└── shared/
    └── middlewares.py      # Middleware de autenticación JWT
```

## 🛠️ Tecnologías Utilizadas

- **FastAPI** - Framework web moderno y rápido
- **SQLite** - Base de datos embebida
- **Strawberry GraphQL** - Librería GraphQL para Python
- **Pydantic** - Validación de datos
- **Uvicorn** - Servidor ASGI

## 📝 Notas

- La base de datos SQLite se crea automáticamente en `src/data/products.db`
- Las 6 categorías de informática se crean automáticamente al iniciar
- El token JWT para pruebas es: `secreto123`
- Solo el endpoint POST de productos requiere autenticación
- GraphQL Playground incluye documentación interactiva
- Los productos pueden estar asociados a una categoría (opcional)

## 🎯 Ejemplos de Uso Completo

### Flujo completo: Crear categoría y agregar productos

```bash
# 1. Ver categorías disponibles
curl http://localhost:8000/categories

# 2. Crear un producto en la categoría "Tarjetas de Video" (ID: 2)
curl -X POST http://localhost:8000/products \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer secreto123" \
  -d '{
    "name": "NVIDIA RTX 4090",
    "price": 1999.99,
    "in_stock": true,
    "currency": "USD",
    "category_id": 2
  }'

# 3. Ver todos los productos de esa categoría
curl http://localhost:8000/categories/2/products

# 4. Consultar en GraphQL con filtro
# Ir a http://localhost:8000/graphql y ejecutar:
# query {
#   products(categoryId: 2) {
#     name
#     price
#     categoryName
#   }
# }
```

## 👤 Autor
DelKira554 y DPBascur

Proyecto de evaluación práctica - Tópicos II
