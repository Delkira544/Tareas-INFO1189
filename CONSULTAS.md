# 📋 Guía Completa de Consultas - API de Productos y Categorías

## 🔧 Configuración

**Base URL:** `http://localhost:8000`  
**GraphQL Playground:** `http://localhost:8000/graphql`  
**Token JWT:** `Bearer secreto123` (requerido solo para POST /products)

---

## 🌐 REST API

### 📦 PRODUCTOS

#### 1. Obtener todos los productos
```bash
curl -X GET "http://localhost:8000/products"
```

#### 2. Obtener productos por categoría
```bash
# Ejemplo: categoría 1
curl -X GET "http://localhost:8000/products?category_id=1"
```

#### 3. Obtener un producto por ID
```bash
# Ejemplo: producto 1
curl -X GET "http://localhost:8000/products/1"
```

#### 4. Crear un nuevo producto (requiere autenticación)
```bash
curl -X POST "http://localhost:8000/products" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer secreto123" \
  -d '{
    "name": "Producto de Prueba",
    "price": 9999.99,
    "in_stock": true,
    "currency": "CLP",
    "category_id": 1
  }'
```

#### 5. Actualizar un producto
```bash
# Ejemplo: actualizar producto 1
curl -X PUT "http://localhost:8000/products/1" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Producto Actualizado",
    "price": 12999.99,
    "in_stock": false
  }'
```

#### 6. Eliminar un producto
```bash
# Ejemplo: eliminar producto 1
curl -X DELETE "http://localhost:8000/products/1"
```

---

### 🏷️ CATEGORÍAS

#### 1. Obtener todas las categorías
```bash
curl -X GET "http://localhost:8000/categories"
```

#### 2. Obtener una categoría por ID
```bash
# Ejemplo: categoría 1
curl -X GET "http://localhost:8000/categories/1"
```

#### 3. Obtener una categoría con sus productos
```bash
# Ejemplo: categoría 1 con productos
curl -X GET "http://localhost:8000/categories/1/products"
```

#### 4. Crear una nueva categoría
```bash
curl -X POST "http://localhost:8000/categories" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Nueva Categoría",
    "description": "Descripción de la nueva categoría"
  }'
```

#### 5. Eliminar una categoría (sin productos asociados)
```bash
# Ejemplo: eliminar categoría 7
curl -X DELETE "http://localhost:8000/categories/7"
```

---

## 🚀 GraphQL API

### 📝 QUERIES (Consultas de Lectura)

#### 1. Obtener todas las categorías
```graphql
query {
  categories {
    id
    name
    description
  }
}
```

#### 2. Obtener todas las categorías con sus productos
```graphql
query {
  categories {
    id
    name
    description
    products {
      id
      name
      price
      in_stock
      currency
    }
  }
}
```

#### 3. Obtener una categoría específica
```graphql
query {
  category(categoryId: 1) {
    id
    name
    description
  }
}
```

#### 4. Obtener una categoría con sus productos
```graphql
query {
  category(categoryId: 1) {
    id
    name
    description
    products {
      id
      name
      price
      in_stock
      currency
    }
  }
}
```

#### 5. Obtener todos los productos
```graphql
query {
  products {
    id
    name
    price
    in_stock
    currency
    categoryId
  }
}
```

#### 6. Obtener productos por categoría
```graphql
query {
  products(categoryId: 1) {
    id
    name
    price
    in_stock
    currency
    categoryId
  }
}
```

#### 7. Obtener productos con información de categoría
```graphql
query {
  products {
    id
    name
    price
    in_stock
    currency
    category {
      id
      name
      description
    }
  }
}
```

#### 8. Obtener un producto específico
```graphql
query {
  product(productId: 1) {
    id
    name
    price
    in_stock
    currency
    categoryId
  }
}
```

#### 9. Obtener un producto con su categoría
```graphql
query {
  product(productId: 1) {
    id
    name
    price
    in_stock
    currency
    category {
      id
      name
      description
    }
  }
}
```

---

### ✏️ MUTATIONS (Operaciones de Escritura)

#### 1. Crear un nuevo producto
```graphql
mutation {
  createProduct(productInput: {
    name: "Producto GraphQL"
    price: 15999.99
    inStock: true
    currency: "CLP"
    categoryId: 1
  }) {
    id
    name
    price
    inStock
    currency
    categoryId
  }
}
```

#### 2. Actualizar un producto
```graphql
mutation {
  updateProduct(
    productId: 1
    productInput: {
      name: "Producto Actualizado GraphQL"
      price: 19999.99
      inStock: false
    }
  ) {
    id
    name
    price
    inStock
    currency
    categoryId
  }
}
```

#### 3. Actualizar solo algunos campos de un producto
```graphql
mutation {
  updateProduct(
    productId: 1
    productInput: {
      price: 24999.99
    }
  ) {
    id
    name
    price
    inStock
    currency
    categoryId
  }
}
```

#### 4. Eliminar un producto
```graphql
mutation {
  deleteProduct(productId: 1)
}
```

#### 5. Crear una nueva categoría
```graphql
mutation {
  createCategory(categoryInput: {
    name: "Categoría GraphQL"
    description: "Descripción desde GraphQL"
  }) {
    id
    name
    description
  }
}
```

#### 6. Eliminar una categoría (sin productos)
```graphql
mutation {
  deleteCategory(categoryId: 7)
}
```

---

## 📊 CONSULTAS COMPLEJAS (GraphQL)

#### 1. Obtener todo: categorías con productos y sus detalles
```graphql
query {
  categories {
    id
    name
    description
    products {
      id
      name
      price
      in_stock
      currency
    }
  }
}
```

#### 2. Búsqueda específica con múltiples categorías
```graphql
query {
  electronics: category(categoryId: 1) {
    name
    products {
      name
      price
    }
  }
  clothing: category(categoryId: 2) {
    name
    products {
      name
      price
    }
  }
}
```

#### 3. Productos de múltiples categorías
```graphql
query {
  electronicsProducts: products(categoryId: 1) {
    name
    price
  }
  clothingProducts: products(categoryId: 2) {
    name
    price
  }
}
```

---

## 🗂️ CATEGORÍAS PREDEFINIDAS

1. **Electrónica** - Dispositivos electrónicos y accesorios
2. **Ropa** - Prendas de vestir y accesorios
3. **Alimentos** - Productos alimenticios
4. **Libros** - Libros físicos y digitales
5. **Hogar** - Artículos para el hogar
6. **Deportes** - Equipamiento deportivo

---

## ⚠️ CASOS DE ERROR

### REST API

#### Error 404 - Producto no encontrado
```bash
curl -X GET "http://localhost:8000/products/999"
# Respuesta: {"detail": "Producto no encontrado"}
```

#### Error 404 - Categoría no encontrada
```bash
curl -X GET "http://localhost:8000/categories/999"
# Respuesta: {"detail": "Categoría no encontrada"}
```

#### Error 400 - Validación fallida (precio negativo)
```bash
curl -X POST "http://localhost:8000/products" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer secreto123" \
  -d '{
    "name": "Producto Inválido",
    "price": -100,
    "in_stock": true,
    "currency": "CLP",
    "category_id": 1
  }'
# Respuesta: {"detail": "El precio debe ser mayor o igual a 0"}
```

#### Error 400 - Nombre muy corto
```bash
curl -X POST "http://localhost:8000/products" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer secreto123" \
  -d '{
    "name": "AB",
    "price": 1000,
    "in_stock": true,
    "currency": "CLP",
    "category_id": 1
  }'
# Respuesta: {"detail": "El nombre debe tener al menos 3 caracteres"}
```

#### Error 400 - Eliminar categoría con productos
```bash
curl -X DELETE "http://localhost:8000/categories/1"
# Respuesta: {"detail": "No se puede eliminar la categoría porque tiene X producto(s) asociado(s)"}
```

#### Error 401 - Sin autorización
```bash
curl -X POST "http://localhost:8000/products" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Producto Test",
    "price": 1000,
    "in_stock": true,
    "currency": "CLP",
    "category_id": 1
  }'
# Respuesta: {"detail": "Token no válido"}
```

### GraphQL

#### Error - Producto no encontrado
```graphql
query {
  product(productId: 999) {
    id
    name
  }
}
# Respuesta: null
```

#### Error - Crear producto con precio negativo
```graphql
mutation {
  createProduct(productInput: {
    name: "Producto Inválido"
    price: -100
    inStock: true
    currency: "CLP"
    categoryId: 1
  }) {
    id
  }
}
# Respuesta: Error con mensaje de validación
```

#### Error - Eliminar categoría con productos
```graphql
mutation {
  deleteCategory(categoryId: 1)
}
# Respuesta: "No se puede eliminar la categoría porque tiene X producto(s) asociado(s)"
```

---

## 🧪 SCRIPT DE PRUEBAS COMPLETO

### Probar todos los endpoints REST con curl

```bash
#!/bin/bash

echo "=== Probando API REST ==="
echo ""

echo "1. GET /products"
curl -s -X GET "http://localhost:8000/products" | jq '.'
echo ""

echo "2. GET /products?category_id=1"
curl -s -X GET "http://localhost:8000/products?category_id=1" | jq '.'
echo ""

echo "3. GET /products/1"
curl -s -X GET "http://localhost:8000/products/1" | jq '.'
echo ""

echo "4. GET /categories"
curl -s -X GET "http://localhost:8000/categories" | jq '.'
echo ""

echo "5. GET /categories/1"
curl -s -X GET "http://localhost:8000/categories/1" | jq '.'
echo ""

echo "6. GET /categories/1/products"
curl -s -X GET "http://localhost:8000/categories/1/products" | jq '.'
echo ""

echo "7. POST /products (crear)"
curl -s -X POST "http://localhost:8000/products" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer secreto123" \
  -d '{
    "name": "Producto Test API",
    "price": 5000,
    "in_stock": true,
    "currency": "CLP",
    "category_id": 1
  }' | jq '.'
echo ""

echo "8. PUT /products/1 (actualizar)"
curl -s -X PUT "http://localhost:8000/products/1" \
  -H "Content-Type: application/json" \
  -d '{
    "price": 6000
  }' | jq '.'
echo ""

echo "=== Pruebas completadas ==="
```

---

## 📚 NOTAS ADICIONALES

### Formato de moneda
- Todos los precios se manejan en **CLP (Pesos Chilenos)**
- Los precios deben ser números positivos (>= 0)

### Validaciones
- **Nombre de producto/categoría**: Mínimo 3 caracteres
- **Precio**: Debe ser >= 0
- **Category ID**: Debe existir en la base de datos

### Integridad referencial
- No se puede eliminar una categoría si tiene productos asociados
- Primero debes eliminar todos los productos de una categoría antes de eliminar la categoría

### Autenticación
- Solo el endpoint `POST /products` requiere autenticación
- Token: `Bearer secreto123`
- Otros endpoints son de acceso público

---

## 🎯 EJEMPLOS DE USO COMÚN

### Caso 1: Crear categoría y agregar productos
```bash
# 1. Crear categoría
curl -X POST "http://localhost:8000/categories" \
  -H "Content-Type: application/json" \
  -d '{"name": "Juguetes", "description": "Juguetes para niños"}'

# 2. Crear producto en esa categoría (asumiendo ID 7)
curl -X POST "http://localhost:8000/products" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer secreto123" \
  -d '{
    "name": "Pelota",
    "price": 2500,
    "in_stock": true,
    "currency": "CLP",
    "category_id": 7
  }'
```

### Caso 2: Actualizar precio de múltiples productos
```bash
# Actualizar producto 1
curl -X PUT "http://localhost:8000/products/1" \
  -H "Content-Type: application/json" \
  -d '{"price": 15000}'

# Actualizar producto 2
curl -X PUT "http://localhost:8000/products/2" \
  -H "Content-Type: application/json" \
  -d '{"price": 18000}'
```

### Caso 3: Consulta completa en GraphQL
```graphql
query {
  # Todas las categorías
  allCategories: categories {
    id
    name
  }
  
  # Productos de electrónica
  electronics: products(categoryId: 1) {
    name
    price
  }
  
  # Detalle de un producto específico
  specificProduct: product(productId: 1) {
    name
    price
    category {
      name
    }
  }
}
```

---

**Última actualización:** Octubre 2025  
**Versión de la API:** 1.0  
**Framework:** FastAPI + Strawberry GraphQL
