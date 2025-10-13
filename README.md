# API Tienda de Informática - Clean Architecture

## 📖 Descripción

API REST y GraphQL para gestionar productos, subcategorías y categorías de una tienda de informática. Implementada siguiendo los principios de **Clean Architecture** con autenticación JWT que expira automáticamente.

### ✨ Características Principales

- **Clean Architecture**: Separación clara de responsabilidades en capas
- **JWT Authentication**: Tokens con expiración automática de 1 hora
- **ACID Transactions**: Propiedades ACID garantizadas en base de datos
- **REST API**: Endpoints tradicionales para operaciones CRUD
- **GraphQL**: Consultas flexibles y específicas
- **Categorización Jerárquica**: Estructura Categoría → Subcategoría → Producto

## 🏗️ Arquitectura del Sistema

```
Clean Architecture Layers:
├── Domain Layer (Entidades de Negocio)
│   ├── entities.py          # Product, Category, Subcategory
│   └── interfaces.py        # Contratos de repositorios
├── Application Layer (Casos de Uso)
│   └── use_cases.py         # Lógica de aplicación
├── Infrastructure Layer (Detalles Técnicos)
│   ├── database.py          # Gestión SQLite con ACID
│   ├── repositories.py      # Implementaciones concretas
│   ├── auth_service.py      # JWT con expiración
│   └── container.py         # Inyección de dependencias
└── Presentation Layer (Interfaces)
    ├── api/                 # REST endpoints
    └── middlewares/         # Autenticación JWT
```

## 🗂️ Estructura de Datos

```
📁 Categoría (ej: "Hardware PC")
└── 📂 Subcategoría (ej: "Tarjetas de Video")
    └── 📄 Producto (ej: "NVIDIA RTX 4090")
```

## 🛠️ Instalación

### Requisitos

- Python 3.12+
- Dependencias en `requirements.txt`

### Pasos de Instalación

1. **Crear entorno virtual:**

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# o
.venv\Scripts\activate     # Windows
```

2. **Instalar dependencias:**

```bash
pip install -r requirements.txt
```

3. **Ejecutar aplicación:**

```bash
cd src
python main.py
```

4. **Poblar datos de ejemplo (opcional):**

```bash
python populate_products.py
```

La API estará disponible en: `http://localhost:8000`

## 🔐 Autenticación JWT

### Obtener Token (Expira en 1 hora)

**Endpoint:** `POST /auth/token`

**Request Body:**

```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response:**

```json
{
  "access_token": "jwt_eyJkYXRhIjp7InVzZXJuYW1lIjoiYWRtaW4iLCJyb2xlIjoiYWRtaW4ifSwiaWF0Ijo...",
  "token_type": "Bearer",
  "expires_in_hours": 1,
  "expires_at": "2024-01-15T11:30:00"
}
```

### Usar Token en Requests

**Header requerido para endpoints protegidos:**

```
Authorization: Bearer jwt_eyJkYXRhIjp7InVzZXJuYW1lIjoiYWRtaW4i...
```

### Validar Token

**Endpoint:** `POST /auth/token/validate?token=tu_token`

**Response (Token válido):**

```json
{
  "message": "Token válido",
  "user_data": {
    "username": "admin",
    "role": "admin"
  },
  "expires_at": "2024-01-15T11:30:00"
}
```

**Response (Token expirado):**

```json
{
  "detail": "Token expirado",
  "error_code": "TOKEN_EXPIRED",
  "message": "El token ha expirado, genera uno nuevo"
}
```

## 📋 API REST Endpoints

### 🏷️ Categorías

#### Listar todas las categorías

**GET** `/categories`

**Response:**

```json
[
  {
    "id": 1,
    "name": "Audio y Video",
    "description": "Equipos de audio, video y streaming",
    "created_at": "2024-01-15T10:30:00"
  }
]
```

#### Obtener categoría por ID

**GET** `/categories/{id}`

**Response:**

```json
{
  "id": 1,
  "name": "Audio y Video",
  "description": "Equipos de audio, video y streaming",
  "created_at": "2024-01-15T10:30:00"
}
```

#### Crear categoría (🔒 Requiere JWT)

**POST** `/categories`

**Request Body:**

```json
{
  "name": "Nueva Categoría",
  "description": "Descripción opcional"
}
```

**Response:**

```json
{
  "id": 7,
  "name": "Nueva Categoría",
  "description": "Descripción opcional",
  "created_at": "2024-01-15T12:00:00"
}
```

### 🔖 Subcategorías

#### Listar todas las subcategorías

**GET** `/subcategories`

**Response:**

```json
[
  {
    "id": 1,
    "name": "Micrófonos",
    "description": "Micrófonos para streaming y grabación",
    "category_id": 1,
    "created_at": "2024-01-15T10:30:00",
    "category": {
      "id": 1,
      "name": "Audio y Video",
      "description": "Equipos de audio, video y streaming"
    }
  }
]
```

#### Obtener subcategorías por categoría

**GET** `/subcategories/category/{category_id}`

**Response:**

```json
[
  {
    "id": 1,
    "name": "Micrófonos",
    "description": "Micrófonos para streaming y grabación",
    "category_id": 1,
    "created_at": "2024-01-15T10:30:00",
    "category": {
      "id": 1,
      "name": "Audio y Video",
      "description": "Equipos de audio, video y streaming"
    }
  }
]
```

#### Crear subcategoría (🔒 Requiere JWT)

**POST** `/subcategories`

**Request Body:**

```json
{
  "name": "Streaming Decks",
  "category_id": 1,
  "description": "Dispositivos para streaming profesional"
}
```

### 📦 Productos

#### Listar todos los productos

**GET** `/products`

**Response:**

```json
[
  {
    "id": 1,
    "name": "Blue Yeti USB",
    "price": 150000,
    "in_stock": true,
    "currency": "CLP",
    "subcategory_id": 1,
    "created_at": "2024-01-15T10:30:00",
    "subcategory": {
      "id": 1,
      "name": "Micrófonos",
      "description": "Micrófonos para streaming y grabación",
      "category_id": 1,
      "category": {
        "id": 1,
        "name": "Audio y Video",
        "description": "Equipos de audio, video y streaming"
      }
    }
  }
]
```

#### Obtener productos disponibles solamente

**GET** `/products?available_only=true`

#### Obtener producto por ID

**GET** `/products/{id}`

**Response:**

```json
{
  "id": 1,
  "name": "Blue Yeti USB",
  "price": 150000,
  "in_stock": true,
  "currency": "CLP",
  "subcategory_id": 1,
  "created_at": "2024-01-15T10:30:00",
  "subcategory": {
    "id": 1,
    "name": "Micrófonos",
    "description": "Micrófonos para streaming y grabación",
    "category_id": 1,
    "category": {
      "id": 1,
      "name": "Audio y Video",
      "description": "Equipos de audio, video y streaming"
    }
  }
}
```

#### Obtener productos por subcategoría

**GET** `/products/subcategory/{subcategory_id}`

#### Obtener productos por categoría

**GET** `/products/category/{category_id}`

#### Crear producto (🔒 Requiere JWT)

**POST** `/products`

**Request Body:**

```json
{
  "name": "iPhone 15 Pro Max",
  "price": 1299000,
  "subcategory_id": 3,
  "in_stock": true,
  "currency": "CLP"
}
```

#### Actualizar producto (🔒 Requiere JWT)

**PUT** `/products/{id}`

**Request Body (campos opcionales):**

```json
{
  "name": "iPhone 15 Pro Max 256GB",
  "price": 1399000,
  "in_stock": false
}
```

#### Aplicar descuento por categoría (🔒 Requiere JWT)

**POST** `/products/category/{category_id}/apply-discount?discount_percentage=15`

**Response:**

```json
{
  "message": "Descuento del 15% aplicado a 8 productos",
  "products_updated": 8,
  "category_id": 1,
  "discount_percentage": 15
}
```

## 🎯 API GraphQL

**Endpoint:** `POST /graphql`
**Playground:** `http://localhost:8000/graphql` (en navegador)

### Queries (Consultas)

#### Obtener todos los productos con estructura completa

```graphql
query {
  products {
    id
    name
    price
    inStock
    currency
    subcategory {
      id
      name
      category {
        id
        name
        description
      }
    }
  }
}
```

#### Obtener producto específico por ID

```graphql
query {
  product(id: 1) {
    id
    name
    price
    subcategory {
      name
      category {
        name
      }
    }
  }
}
```

#### Obtener productos por categoría

```graphql
query {
  productsByCategory(categoryId: 1) {
    id
    name
    price
    subcategory {
      name
    }
  }
}
```

#### Obtener solo productos disponibles

```graphql
query {
  availableProducts {
    id
    name
    price
    inStock
  }
}
```

#### Obtener todas las categorías

```graphql
query {
  categories {
    id
    name
    description
  }
}
```

#### Obtener subcategorías con información de categoría

```graphql
query {
  subcategories {
    id
    name
    category {
      id
      name
    }
  }
}
```

#### Obtener subcategorías por categoría

```graphql
query {
  subcategoriesByCategory(categoryId: 1) {
    id
    name
    description
  }
}
```

### Mutations (Modificaciones) 🔒 Requieren JWT

#### Crear producto

```graphql
mutation {
  createProduct(
    input: {
      name: "NVIDIA RTX 4090"
      price: 2500000
      subcategoryId: 4
      inStock: true
      currency: "CLP"
    }
  ) {
    id
    name
    price
    subcategory {
      name
      category {
        name
      }
    }
  }
}
```

#### Crear categoría

```graphql
mutation {
  createCategory(
    input: {
      name: "Impresoras 3D"
      description: "Impresoras y accesorios de impresión 3D"
    }
  ) {
    id
    name
    description
  }
}
```

#### Crear subcategoría

```graphql
mutation {
  createSubcategory(
    input: {
      name: "Impresoras FDM"
      categoryId: 7
      description: "Impresoras de filamento"
    }
  ) {
    id
    name
    category {
      name
    }
  }
}
```

#### Aplicar descuento por categoría

```graphql
mutation {
  applyDiscountToCategory(categoryId: 2, discountPercentage: 20)
}
```

#### Eliminar producto

```graphql
mutation {
  deleteProduct(id: 1)
}
```

## � Endpoints de Información

### Estado de la aplicación

**GET** `/health`

**Response:**

```json
{
  "status": "healthy",
  "version": "2.0.0",
  "database": "connected",
  "container": {
    "status": "healthy",
    "repositories": {
      "category": "SQLiteCategoryRepository",
      "subcategory": "SQLiteSubcategoryRepository",
      "product": "SQLiteProductRepository"
    }
  },
  "features": {
    "jwt_expiration": "1 hour",
    "database": "SQLite with ACID",
    "architecture": "Clean Architecture"
  }
}
```

### Información general

**GET** `/`

**Response:**

```json
{
  "message": "Products API - Clean Architecture",
  "version": "2.0.0",
  "description": "API para gestión de productos con categorías y subcategorías",
  "features": [
    "Clean Architecture",
    "JWT Authentication con expiración",
    "REST API",
    "GraphQL",
    "ACID Transactions",
    "Categorización jerárquica"
  ],
  "endpoints": {
    "auth": "/auth/token",
    "categories": "/categories",
    "subcategories": "/subcategories",
    "products": "/products",
    "graphql": "/graphql",
    "docs": "/docs",
    "health": "/health"
  },
  "structure": "Categoría -> Subcategoría -> Producto"
}
```

## 📱 Ejemplos de Uso Completo

### 1. Flujo de Autenticación y Creación

```
# 1. Generar token JWT
POST /auth/token
Body: {"username": "admin", "password": "admin123"}

# 2. Usar token para crear categoría
POST /categories
Headers: Authorization: Bearer {token}
Body: {"name": "Gaming", "description": "Productos para gaming"}

# 3. Crear subcategoría
POST /subcategories
Headers: Authorization: Bearer {token}
Body: {"name": "Periféricos Gaming", "category_id": 7}

# 4. Crear producto
POST /products
Headers: Authorization: Bearer {token}
Body: {
  "name": "Razer DeathAdder V3",
  "price": 65000,
  "subcategory_id": 19,
  "currency": "CLP"
}
```

### 2. Consultas GraphQL Complejas

```graphql
# Consulta completa con toda la jerarquía
query CompleteProductInfo {
  products {
    id
    name
    price
    inStock
    currency
    createdAt
    subcategory {
      id
      name
      description
      category {
        id
        name
        description
      }
    }
  }
}

# Filtrar productos caros por categoría
query ExpensiveProductsByCategory {
  productsByCategory(categoryId: 2) {
    id
    name
    price
    subcategory {
      name
    }
  }
}
```

## 🛡️ Endpoints Protegidos

Los siguientes endpoints requieren autenticación JWT:

- `POST /products` - Crear producto
- `PUT /products/{id}` - Actualizar producto
- `DELETE /products/{id}` - Eliminar producto
- `POST /categories` - Crear categoría
- `DELETE /categories/{id}` - Eliminar categoría
- `POST /subcategories` - Crear subcategoría
- `DELETE /subcategories/{id}` - Eliminar subcategoría
- `POST /graphql` - Mutaciones GraphQL

## 📊 Datos Predefinidos

La aplicación incluye:

- **6 Categorías**: Audio y Video, Hardware PC, Almacenamiento, Periféricos, Monitores, Redes
- **18 Subcategorías**: Micrófonos, Tarjetas de Video, SSD, Teclados, etc.
- **30+ Productos de ejemplo** (usando `populate_products.py`)

## 📁 Estructura del Proyecto

```
src/
├── main.py                          # Aplicación FastAPI principal
├── populate_products.py             # Script para poblar datos de ejemplo
├── domain/
│   ├── __init__.py
│   ├── entities.py                  # Product, Category, Subcategory
│   └── interfaces.py                # Contratos de repositorios
├── application/
│   ├── __init__.py
│   └── use_cases.py                 # Casos de uso (lógica de aplicación)
├── infrastructure/
│   ├── __init__.py
│   ├── database.py                  # Gestión SQLite con ACID
│   ├── repositories.py              # Implementaciones concretas
│   ├── auth_service.py              # JWT con expiración
│   └── container.py                 # Inyección de dependencias
└── presentation/
    ├── __init__.py
    ├── api/
    │   ├── __init__.py
    │   ├── auth_routes.py           # Endpoints de autenticación
    │   ├── categories_routes.py     # Endpoints REST de categorías
    │   ├── subcategories_routes.py  # Endpoints REST de subcategorías
    │   ├── products_routes.py       # Endpoints REST de productos
    │   └── graphql_routes.py        # API GraphQL
    └── middlewares/
        ├── __init__.py
        └── auth.py                  # Middleware de autenticación JWT
```

## 🗃️ Base de Datos

- **Motor:** SQLite con propiedades ACID
- **Ubicación:** `src/data/products.db`
- **Inicialización:** Automática al arrancar la aplicación
- **Foreign Keys:** Habilitadas para integridad referencial

## 🚀 Tecnologías

- **FastAPI** - Framework web moderno y rápido
- **SQLite** - Base de datos embebida con ACID
- **Strawberry GraphQL** - Librería GraphQL para Python
- **Pydantic** - Validación de datos
- **Clean Architecture** - Principios de arquitectura limpia
- **JWT** - Autenticación con tokens

## � Autores

**DelKira554** y **DPBascur**

_Proyecto de evaluación práctica - Tópicos II_

---

## 📚 Documentación Interactiva

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`
- **GraphQL Playground:** `http://localhost:8000/graphql`
