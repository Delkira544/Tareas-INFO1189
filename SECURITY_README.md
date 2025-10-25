# 🔐 OWASP Top 10 Security Implementation

Esta implementación integra **OWASP Top 10 2021** completo en tu API de productos con Clean Architecture.

## 🎯 Resumen de Implementación

### ✅ OWASP Top 10 Cubiertos:

| OWASP ID | Vulnerabilidad            | Implementación                  | Archivo                |
| -------- | ------------------------- | ------------------------------- | ---------------------- |
| **A01**  | Broken Access Control     | Role-based middleware + JWT     | `rolemiddleware.py`    |
| **A02**  | Cryptographic Failures    | Secure hashing + encryption     | `security_service.py`  |
| **A03**  | Injection                 | Query sanitization + validation | `query_sanitizer.py`   |
| **A04**  | Insecure Design           | Security-by-design patterns     | `security_config.py`   |
| **A05**  | Security Misconfiguration | Centralized config              | `security_config.py`   |
| **A06**  | Vulnerable Components     | Security headers                | `security_headers.py`  |
| **A07**  | Identity Failures         | Enhanced JWT security           | `auth_service.py`      |
| **A08**  | Software Integrity        | File integrity checking         | `integrity_checker.py` |
| **A09**  | Security Logging          | Comprehensive logging           | `security_logger.py`   |
| **A10**  | SSRF                      | Request validation              | `query_sanitizer.py`   |

### 🧪 5 Pruebas API Implementadas:

1. **Authentication & Authorization Test** - Control de acceso y JWT
2. **Input Validation & SQL Injection Test** - Prevención de inyecciones
3. **JWT Security & Session Management Test** - Seguridad de tokens
4. **Rate Limiting & DoS Prevention Test** - Protección contra DoS
5. **Complete Security Workflow Test** - Flujo completo de seguridad

## 🚀 Cómo Ejecutar

### Opción 1: Script Automático (Recomendado)

```bash
# Hacer el script ejecutable
chmod +x run_security_tests.sh

# Ejecutar todas las pruebas automáticamente
./run_security_tests.sh
```

### Opción 2: Manual

```bash
# 1. Instalar dependencias
pip install requests

# 2. Iniciar la API
cd src
python main.py &

# 3. Ejecutar pruebas (en otra terminal)
python test_api_security.py

# 4. Ejecutar prueba específica
python test_api_security.py --test 1  # Solo test de autenticación
```

## 📁 Archivos Nuevos Creados

### Infrastructure (Seguridad)

```
src/infrastructure/
├── security_config.py      # Configuración centralizada
├── security_service.py     # Servicios criptográficos
├── security_logger.py      # Logging de eventos
├── integrity_checker.py    # Verificador de integridad
└── query_sanitizer.py      # Sanitización anti-injection
```

### Middleware (Seguridad)

```
src/presentation/middlewares/
└── security_headers.py     # Headers de seguridad HTTP
```

### Tests y Scripts

```
├── test_api_security.py    # Suite de 5 pruebas API
├── run_security_tests.sh   # Script de ejecución automática
└── SECURITY_README.md      # Este archivo
```

## 🔧 Configuraciones de Seguridad

### Headers de Seguridad Aplicados:

- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=31536000`
- `Content-Security-Policy: default-src 'self'`

### Rate Limiting:

- **100 requests por minuto** por IP
- **Bloqueo automático** de IPs sospechosas

### JWT Security:

- **Expiración**: 1 hora
- **Algoritmo**: HS256
- **Validación**: Automática en rutas protegidas

### Input Validation:

- **SQL Injection**: Detectado y bloqueado
- **XSS**: Sanitización automática
- **Tamaño máximo**: 1MB por payload

## 📊 Monitoreo de Seguridad

### Logs Generados:

- `security.log` - Eventos de seguridad en tiempo real
- `integrity_checksums.json` - Baseline de integridad de archivos

### Endpoints de Monitoreo:

- `GET /health` - Estado completo con métricas de seguridad
- `GET /` - Información de características de seguridad

## 🛡️ Rutas Protegidas

### Requieren JWT Token:

- `POST /products` - Crear producto
- `PUT /products/{id}` - Actualizar producto
- `DELETE /products/{id}` - Eliminar producto
- `POST /graphql` - Mutaciones GraphQL

### Requieren Rol Admin:

- `DELETE /categories/{id}` - Eliminar categoría
- `DELETE /subcategories/{id}` - Eliminar subcategoría

## 🔍 Verificación Manual

### 1. Verificar Headers de Seguridad:

```bash
curl -I http://localhost:8000/health
```

### 2. Test de SQL Injection:

```bash
curl "http://localhost:8000/products/1'; DROP TABLE products; --"
```

### 3. Test de Rate Limiting:

```bash
for i in {1..110}; do curl http://localhost:8000/products; done
```

### 4. Test de JWT:

```bash
# Sin token (debe fallar)
curl -X POST http://localhost:8000/products

# Con token inválido (debe fallar)
curl -X POST http://localhost:8000/products \
  -H "Authorization: Bearer invalid_token"

# Con token válido (debe funcionar)
TOKEN=$(curl -X POST http://localhost:8000/auth/token \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | jq -r .access_token)

curl -X POST http://localhost:8000/products \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","price":100,"subcategory_id":1}'
```

## 📈 Resultados Esperados

Al ejecutar `./run_security_tests.sh`, deberías ver:

```
🔐 OWASP Top 10 Security Testing Suite
======================================

✅ Todas las dependencias están disponibles
✅ Estructura del proyecto verificada
✅ API disponible en http://localhost:8000

🧪 TEST 1: Authentication & Authorization
✅ PASS 1.1 - Acceso sin token denegado
✅ PASS 1.2 - Token inválido rechazado
✅ PASS 1.3 - Obtención de token válido
✅ PASS 1.4 - Token válido permite acceso
✅ PASS 1.5 - Endpoints públicos funcionan

... (más pruebas) ...

🎉 TODAS LAS PRUEBAS DE SEGURIDAD PASARON EXITOSAMENTE
✅ OWASP Top 10 verificado
✅ 5 pruebas API completadas
```

## 🚨 Solución de Problemas

### Error: "API no disponible"

```bash
# Verificar que la API esté corriendo
ps aux | grep python

# Verificar puerto
netstat -tlnp | grep 8000

# Revisar logs
tail -f src/security.log
```

### Error: "Dependencias faltantes"

```bash
# Instalar todas las dependencias
pip install -r requirements.txt
pip install requests
```

### Error: "Archivos faltantes"

- Verifica que todos los archivos de `src/infrastructure/` existan
- Ejecuta git pull para obtener la última versión

## 🎯 Próximos Pasos

1. **Configurar Environment Variables**:

   ```bash
   export JWT_SECRET_KEY="tu_clave_super_secreta_aqui"
   ```

2. **Configurar HTTPS en producción**

3. **Implementar WAF (Web Application Firewall)**

4. **Configurar monitoring con Prometheus/Grafana**

5. **Implementar backup automático de logs de seguridad**

## 📞 Soporte

Si tienes problemas:

1. Revisa `security.log` para eventos de seguridad
2. Ejecuta pruebas individuales: `python test_api_security.py --test 1`
3. Verifica la documentación en `http://localhost:8000/docs`

---

**¡Tu API ahora está protegida con OWASP Top 10 2021!** 🛡️
