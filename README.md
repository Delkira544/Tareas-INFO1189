# Tareas-INFO1189

## Evaluación Práctica: API REST y GraphQL de Productos

Proyecto que implementa una API completa de gestión de productos usando FastAPI con endpoints REST y GraphQL.

## ✨ Características Implementadas

### 1. API REST - Endpoints de Productos
- ✅ **GET /products** - Obtener todos los productos
- ✅ **GET /products/{id}** - Obtener producto por ID
- ✅ **POST /products** - Crear nuevo producto (Protegido con JWT)
- ✅ **PUT /products/{id}** - Actualizar producto completo
- ✅ **PATCH /products/{id}** - Actualizar producto parcialmente
- ✅ **DELETE /products/{id}** - Eliminar producto

### 2. Autenticación JWT
- ✅ Middleware de autenticación condicional
- ✅ Protección del endpoint POST con Bearer Token
- ✅ Token: `Bearer secreto123`

### 3. API GraphQL
- ✅ **Query products** - Obtener todos los productos
- ✅ **Query product(productId: Int!)** - Obtener producto por ID
- ✅ **Mutation createProduct** - Crear nuevo producto
- ✅ **Mutation updateProduct** - Actualizar producto
- ✅ **Mutation deleteProduct** - Eliminar producto

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

### API REST

#### Obtener todos los productos
```bash
curl http://localhost:8000/products
```

#### Crear un producto (requiere token JWT)
```bash
curl -X POST http://localhost:8000/products \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer secreto123" \
  -d '{
    "name": "Laptop",
    "price": 999.99,
    "in_stock": true,
    "currency": "USD"
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

#### Query: Obtener todos los productos
```graphql
query {
  products {
    id
    name
    price
    inStock
    currency
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
  }
}
```

#### Mutation: Crear producto
```graphql
mutation {
  createProduct(input: {
    name: "Laptop"
    price: 999.99
    inStock: true
    currency: "USD"
  }) {
    id
    name
    price
    inStock
    currency
  }
}
```

#### Mutation: Actualizar producto
```graphql
mutation {
  updateProduct(productId: 1, input: {
    price: 899.99
  }) {
    id
    name
    price
    inStock
    currency
  }
}
```

#### Mutation: Eliminar producto
```graphql
mutation {
  deleteProduct(productId: 1)
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
│   ├── models.py           # Modelos de datos
│   ├── repository.py       # Acceso a datos
│   └── routes.py           # Endpoints REST
├── graphql/
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

- La base de datos SQLite se crea automáticamente en `data/products.db`
- El token JWT para pruebas es: `secreto123`
- Solo el endpoint POST de productos requiere autenticación
- GraphQL Playground incluye documentación interactiva

## 👤 Autor

Proyecto de evaluación práctica - Tópicos II
