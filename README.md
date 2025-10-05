# Tareas-INFO1189

## Evaluación Práctica: API REST y GraphQL de Productos

Proyecto que implementa una API completa de gestión de productos de informática usando FastAPI con endpoints REST y GraphQL, incluyendo sistema de categorías.

## ✨ Características Implementadas

### 1. API REST - Endpoints de Productos
- ✅ **GET /products** - Obtener todos los productos
- ✅ **GET /products/{id}** - Obtener producto por ID
- ✅ **POST /products** - Crear nuevo producto (Protegido con JWT)
- ✅ **PUT /products/{id}** - Actualizar producto completo
- ✅ **PATCH /products/{id}** - Actualizar producto parcialmente
- ✅ **DELETE /products/{id}** - Eliminar producto

### 2. API REST - Endpoints de Categorías
- ✅ **GET /categories** - Obtener todas las categorías
- ✅ **GET /categories/{id}** - Obtener categoría por ID
- ✅ **GET /categories/{id}/products** - Obtener productos de una categoría
- ✅ **POST /categories** - Crear nueva categoría
- ✅ **DELETE /categories/{id}** - Eliminar categoría

### 3. Categorías Predefinidas (Informática)
- 🎤 **Micrófonos** - Micrófonos para streaming y grabación
- 🎮 **Tarjetas de Video** - GPUs y tarjetas gráficas
- 💾 **Memorias RAM** - Módulos de memoria RAM
- 🔧 **Placas Madres** - Motherboards y placas base
- 💿 **Discos Duros** - HDDs, SSDs y almacenamiento
- ⚡ **Fuentes de Poder** - PSUs y fuentes de alimentación

### 4. Autenticación JWT
- ✅ Middleware de autenticación condicional
- ✅ Protección del endpoint POST con Bearer Token
- ✅ Token: `Bearer secreto123`

### 5. API GraphQL
- ✅ **Query categories** - Obtener todas las categorías
- ✅ **Query category(categoryId)** - Obtener categoría por ID
- ✅ **Query products** - Obtener todos los productos (con filtro opcional por categoría)
- ✅ **Query product(productId)** - Obtener producto por ID
- ✅ **Mutation createCategory** - Crear nueva categoría
- ✅ **Mutation createProduct** - Crear nuevo producto
- ✅ **Mutation updateProduct** - Actualizar producto
- ✅ **Mutation deleteProduct** - Eliminar producto
- ✅ **Mutation deleteCategory** - Eliminar categoría

## 🚀 Instalación y Ejecución

### 1. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 2. Ejecutar el servidor
```bash
cd src
uvicorn main:app --reload
```

El servidor estará disponible en: `http://localhost:8000`

## 📖 Uso de la API

### API REST - Categorías

#### Obtener todas las categorías
```bash
curl http://localhost:8000/categories
```

#### Obtener productos de una categoría específica
```bash
# Ejemplo: Productos de "Tarjetas de Video" (ID: 2)
curl http://localhost:8000/categories/2/products
```

#### Crear una nueva categoría
```bash
curl -X POST http://localhost:8000/categories \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Procesadores",
    "description": "CPUs Intel y AMD"
  }'
```

### API REST - Productos

#### Obtener todos los productos
```bash
curl http://localhost:8000/products
```

#### Crear un producto con categoría (requiere token JWT)
```bash
curl -X POST http://localhost:8000/products \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer secreto123" \
  -d '{
    "name": "RTX 4090",
    "price": 1999.99,
    "in_stock": true,
    "currency": "USD",
    "category_id": 2
  }'
```

#### Actualizar producto (PUT)
```bash
curl -X PUT http://localhost:8000/products/1 \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Laptop Gaming",
    "price": 1299.99,
    "in_stock": true,
    "currency": "USD"
  }'
```

#### Actualizar parcial (PATCH)
```bash
curl -X PATCH http://localhost:8000/products/1 \
  -H "Content-Type: application/json" \
  -d '{
    "price": 899.99
  }'
```

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
