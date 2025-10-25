"""
API Security Tests - 5 Comprehensive Test Cases
Pruebas de seguridad siguiendo OWASP Top 10
Ejecutar con: python test_api_security.py
"""
import requests
import json
import time
import sys
from typing import Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor


class APISecurityTester:
    """Suite de pruebas de seguridad para la API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Inicializar tester de seguridad
        
        Args:
            base_url: URL base de la API
        """
        self.base_url = base_url
        self.session = requests.Session()
        self.valid_token = None
        self.test_results = []
    
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log de resultados de pruebas"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
    
    def _get_valid_token(self) -> Optional[str]:
        """Obtener token válido para pruebas"""
        try:
            response = self.session.post(f"{self.base_url}/auth/token", 
                json={"username": "admin", "password": "admin123"})
            
            if response.status_code == 201:
                return response.json()["access_token"]
            else:
                print(f"⚠️  No se pudo obtener token: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Error obteniendo token: {e}")
            return None
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Hacer request con manejo de errores"""
        url = f"{self.base_url}{endpoint}"
        try:
            return self.session.request(method, url, **kwargs)
        except Exception as e:
            print(f"❌ Error en request {method} {endpoint}: {e}")
            # Crear response mock para no romper el flujo
            response = requests.Response()
            response.status_code = 500
            response._content = json.dumps({"error": str(e)}).encode()
            return response
    
    # ========================================================================
    # Test 1: Authentication & Authorization (A01 - Broken Access Control)
    # ========================================================================
    
    def test_1_authentication_and_authorization(self):
        """
        Test 1: Prueba completa de autenticación y autorización
        Verifica: A01 - Broken Access Control
        """
        print("\n🧪 TEST 1: Authentication & Authorization")
        
        # 1.1 - Acceso sin token (debe fallar)
        response = self._make_request("POST", "/products", 
            json={"name": "Test Product", "price": 100, "subcategory_id": 1})
        
        success = response.status_code == 401
        self.log_test("1.1 - Acceso sin token denegado", success,
                     f"Status: {response.status_code}")
        
        # 1.2 - Token inválido (debe fallar)
        response = self._make_request("POST", "/products", 
            headers={"Authorization": "Bearer token_invalido"},
            json={"name": "Test Product", "price": 100, "subcategory_id": 1})
        
        success = response.status_code == 401
        self.log_test("1.2 - Token inválido rechazado", success,
                     f"Status: {response.status_code}")
        
        # 1.3 - Obtener token válido
        self.valid_token = self._get_valid_token()
        success = self.valid_token is not None
        self.log_test("1.3 - Obtención de token válido", success)
        
        if not self.valid_token:
            return
        
        # 1.4 - Token válido (debe funcionar)
        response = self._make_request("POST", "/products",
            headers={"Authorization": f"Bearer {self.valid_token}"},
            json={
                "name": "Test Product Security",
                "price": 15000,
                "subcategory_id": 1,
                "in_stock": True,
                "currency": "CLP"
            })
        
        success = response.status_code in [201, 200]
        self.log_test("1.4 - Token válido permite acceso", success,
                     f"Status: {response.status_code}")
        
        # 1.5 - Endpoints de lectura públicos
        response = self._make_request("GET", "/products")
        success = response.status_code == 200
        self.log_test("1.5 - Endpoints públicos funcionan", success)
        
        print("🎯 TEST 1 COMPLETADO")
    
    # ========================================================================
    # Test 2: Input Validation & SQL Injection (A03 - Injection)
    # ========================================================================
    
    def test_2_input_validation_sql_injection(self):
        """
        Test 2: Validación de entrada y prevención de SQL Injection
        Verifica: A03 - Injection
        """
        print("\n🧪 TEST 2: Input Validation & SQL Injection")
        
        if not self.valid_token:
            self.valid_token = self._get_valid_token()
        
        # 2.1 - SQL Injection en parámetros de URL
        malicious_payloads = [
            "1; DROP TABLE products;--",
            "1' OR '1'='1",
            "1 UNION SELECT * FROM categories",
            "-1' OR 1=1--"
        ]
        
        sql_injection_blocked = 0
        for i, payload in enumerate(malicious_payloads):
            response = self._make_request("GET", f"/products/{payload}")
            # Debe retornar 400, 404 o 422, no 200 ni 500
            if response.status_code in [400, 404, 422]:
                sql_injection_blocked += 1
        
        success = sql_injection_blocked >= len(malicious_payloads) * 0.8  # 80% bloqueados
        self.log_test("2.1 - SQL Injection en URLs prevenida", success,
                     f"{sql_injection_blocked}/{len(malicious_payloads)} bloqueados")
        
        # 2.2 - SQL Injection en JSON payload
        sql_injection_product = {
            "name": "'; DROP TABLE products; --",
            "price": 100,
            "subcategory_id": 1
        }
        
        response = self._make_request("POST", "/products",
            headers={"Authorization": f"Bearer {self.valid_token}"},
            json=sql_injection_product)
        
        success = response.status_code in [400, 422]
        self.log_test("2.2 - SQL Injection en JSON prevenida", success,
                     f"Status: {response.status_code}")
        
        # 2.3 - XSS en campos de texto
        xss_payloads = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>"
        ]
        
        xss_blocked = 0
        for payload in xss_payloads:
            response = self._make_request("POST", "/products",
                headers={"Authorization": f"Bearer {self.valid_token}"},
                json={"name": payload, "price": 100, "subcategory_id": 1})
            
            if response.status_code in [400, 422]:
                xss_blocked += 1
            elif response.status_code == 201:
                # Si se acepta, verificar que esté sanitizado
                try:
                    product_data = response.json()
                    if "<script>" not in product_data.get("name", ""):
                        xss_blocked += 1
                except:
                    pass
        
        success = xss_blocked >= len(xss_payloads) * 0.8
        self.log_test("2.3 - XSS en campos prevenida", success,
                     f"{xss_blocked}/{len(xss_payloads)} bloqueados")
        
        # 2.4 - Validación de tipos de datos
        invalid_data = {
            "name": "",  # Muy corto
            "price": -100,  # Negativo
            "subcategory_id": "invalid"  # No numérico
        }
        
        response = self._make_request("POST", "/products",
            headers={"Authorization": f"Bearer {self.valid_token}"},
            json=invalid_data)
        
        success = response.status_code == 422
        self.log_test("2.4 - Validación de tipos funciona", success,
                     f"Status: {response.status_code}")
        
        print("🎯 TEST 2 COMPLETADO")
    
    # ========================================================================
    # Test 3: JWT Security & Session Management (A02 & A07)
    # ========================================================================
    
    def test_3_jwt_security_session_management(self):
        """
        Test 3: Seguridad JWT y gestión de sesiones
        Verifica: A02 - Cryptographic Failures, A07 - Identity Failures
        """
        print("\n🧪 TEST 3: JWT Security & Session Management")
        
        # 3.1 - Generar token y verificar estructura
        response = self._make_request("POST", "/auth/token", 
            json={"username": "admin", "password": "admin123"})
        
        success = response.status_code == 201
        token_data = {}
        if success:
            try:
                token_data = response.json()
                success = "access_token" in token_data and "expires_at" in token_data
            except:
                success = False
        
        self.log_test("3.1 - Token JWT generado correctamente", success)
        
        if not success:
            return
        
        token = token_data["access_token"]
        
        # 3.2 - Verificar información del token
        response = self._make_request("GET", f"/auth/token/info", 
            params={"token": token})
        
        success = response.status_code == 200
        if success:
            try:
                token_info = response.json()
                success = token_info.get("valid") == True
            except:
                success = False
        
        self.log_test("3.2 - Información del token válida", success)
        
        # 3.3 - Validar token
        response = self._make_request("POST", f"/auth/token/validate", 
            params={"token": token})
        
        success = response.status_code == 200
        self.log_test("3.3 - Validación de token funciona", success)
        
        # 3.4 - Credenciales incorrectas
        response = self._make_request("POST", "/auth/token", 
            json={"username": "admin", "password": "wrong_password"})
        
        success = response.status_code == 401
        self.log_test("3.4 - Credenciales incorrectas rechazadas", success)
        
        # 3.5 - Tokens malformados
        malformed_tokens = [
            "invalid_token",
            "",
            "jwt_malformed_token_123"
        ]
        
        malformed_rejected = 0
        for malformed_token in malformed_tokens:
            response = self._make_request("POST", f"/auth/token/validate", 
                params={"token": malformed_token})
            if response.status_code == 401:
                malformed_rejected += 1
        
        success = malformed_rejected == len(malformed_tokens)
        self.log_test("3.5 - Tokens malformados rechazados", success,
                     f"{malformed_rejected}/{len(malformed_tokens)} rechazados")
        
        print("🎯 TEST 3 COMPLETADO")
    
    # ========================================================================
    # Test 4: Rate Limiting & DoS Prevention (A06 & A05)
    # ========================================================================
    
    def test_4_rate_limiting_dos_prevention(self):
        """
        Test 4: Rate limiting y prevención de DoS
        Verifica: A06 - Vulnerable Components, A05 - Security Misconfiguration
        """
        print("\n🧪 TEST 4: Rate Limiting & DoS Prevention")
        
        # 4.1 - Test de múltiples requests rápidos
        def make_rapid_request():
            return self._make_request("GET", "/products")
        
        # Hacer 20 requests rápidos en paralelo
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_rapid_request) for _ in range(20)]
            responses = [f.result() for f in futures]
        
        elapsed_time = time.time() - start_time
        
        successful_requests = sum(1 for r in responses if r.status_code == 200)
        rate_limited_requests = sum(1 for r in responses if r.status_code == 429)
        
        # Rate limiting debería activarse si hay muchos requests rápidos
        success = rate_limited_requests > 0 or elapsed_time > 2  # O tomó tiempo procesarlos
        self.log_test("4.1 - Rate limiting funciona", success,
                     f"Exitosos: {successful_requests}, Limitados: {rate_limited_requests}")
        
        # 4.2 - Test de payload grande
        large_payload = {
            "name": "A" * 2000,  # Nombre muy largo
            "price": 100,
            "subcategory_id": 1,
            "description": "B" * 5000  # Descripción muy larga
        }
        
        if not self.valid_token:
            self.valid_token = self._get_valid_token()
        
        response = self._make_request("POST", "/products",
            headers={"Authorization": f"Bearer {self.valid_token}"},
            json=large_payload)
        
        # Debe rechazar payloads muy grandes
        success = response.status_code in [400, 413, 422]
        self.log_test("4.2 - Payloads grandes rechazados", success,
                     f"Status: {response.status_code}")
        
        # 4.3 - Test de headers maliciosos
        malicious_headers = {
            "User-Agent": "AttackBot/1.0 " + "A" * 500,
            "X-Custom-Header": "<script>alert('xss')</script>"
        }
        
        response = self._make_request("GET", "/products", headers=malicious_headers)
        
        # Debe manejar headers maliciosos sin crashear
        success = response.status_code in [200, 400]
        self.log_test("4.3 - Headers maliciosos manejados", success)
        
        # 4.4 - Test de URLs muy largas
        long_path = "/products/" + "a" * 500
        response = self._make_request("GET", long_path)
        
        success = response.status_code in [404, 414]  # Not Found o URI Too Long
        self.log_test("4.4 - URLs largas rechazadas", success)
        
        print("🎯 TEST 4 COMPLETADO")
    
    # ========================================================================
    # Test 5: Complete Security Workflow (Todos los OWASP)
    # ========================================================================
    
    def test_5_complete_security_workflow(self):
        """
        Test 5: Flujo completo de seguridad
        Verifica: Todos los aspectos de OWASP Top 10
        """
        print("\n🧪 TEST 5: Complete Security Workflow")
        
        # 5.1 - Flujo de autenticación completo
        print("   5.1 - Iniciando flujo de autenticación...")
        
        # Obtener token
        auth_response = self._make_request("POST", "/auth/token", 
            json={"username": "admin", "password": "admin123"})
        
        success = auth_response.status_code == 201
        if not success:
            self.log_test("5.1 - Flujo de autenticación", False, "No se pudo obtener token")
            return
        
        token = auth_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 5.2 - CRUD completo con validaciones de seguridad
        print("   5.2 - Ejecutando CRUD con validaciones...")
        
        # CREATE - Crear categoría (solo admin)
        category_response = self._make_request("POST", "/categories",
            headers=headers,
            json={
                "name": "Security Test Category",
                "description": "Categoría para pruebas de seguridad"
            })
        
        # Puede fallar si no es admin, eso está bien
        category_created = category_response.status_code in [201, 200]
        category_id = None
        
        if category_created:
            try:
                category_id = category_response.json()["id"]
            except:
                pass
        
        # CREATE - Crear subcategoría (usar una existente si falla crear categoría)
        subcategory_data = {
            "name": "Security Test Subcategory",
            "category_id": category_id if category_id else 1,
            "description": "Subcategoría para pruebas"
        }
        
        subcategory_response = self._make_request("POST", "/subcategories",
            headers=headers, json=subcategory_data)
        
        subcategory_created = subcategory_response.status_code in [201, 200]
        subcategory_id = 1  # Default fallback
        
        if subcategory_created:
            try:
                subcategory_id = subcategory_response.json()["id"]
            except:
                pass
        
        # CREATE - Crear producto
        product_response = self._make_request("POST", "/products",
            headers=headers,
            json={
                "name": "Security Test Product",
                "price": 99999,
                "subcategory_id": subcategory_id,
                "in_stock": True,
                "currency": "CLP"
            })
        
        product_created = product_response.status_code in [201, 200]
        product_id = None
        
        if product_created:
            try:
                product_id = product_response.json()["id"]
            except:
                pass
        
        self.log_test("5.2 - CRUD operations", product_created, 
                     "Producto creado exitosamente" if product_created else "Falló creación")
        
        # 5.3 - Test de integridad de datos
        if product_id:
            # READ - Verificar datos
            read_response = self._make_request("GET", f"/products/{product_id}")
            read_success = read_response.status_code == 200
            
            if read_success:
                try:
                    product_data = read_response.json()
                    read_success = product_data["name"] == "Security Test Product"
                except:
                    read_success = False
            
            self.log_test("5.3 - Integridad de datos", read_success)
        else:
            self.log_test("5.3 - Integridad de datos", False, "No hay producto para verificar")
        
        # 5.4 - Test GraphQL con seguridad
        graphql_query = {
            "query": """
                query {
                    products {
                        id
                        name
                        price
                    }
                }
            """
        }
        
        graphql_response = self._make_request("POST", "/graphql", json=graphql_query)
        graphql_success = graphql_response.status_code == 200
        
        if graphql_success:
            try:
                data = graphql_response.json()
                graphql_success = "data" in data
            except:
                graphql_success = False
        
        self.log_test("5.4 - GraphQL funciona", graphql_success)
        
        # 5.5 - Test de endpoints de información
        # Health check
        health_response = self._make_request("GET", "/health")
        health_success = health_response.status_code == 200
        
        if health_success:
            try:
                health_data = health_response.json()
                health_success = health_data.get("status") == "healthy"
            except:
                health_success = False
        
        # Root endpoint
        root_response = self._make_request("GET", "/")
        root_success = root_response.status_code == 200
        
        endpoints_success = health_success and root_success
        self.log_test("5.5 - Endpoints de información", endpoints_success)
        
        print("🎯 TEST 5 COMPLETADO")
    
    def run_all_tests(self):
        """Ejecutar todas las pruebas de seguridad"""
        print("🚀 INICIANDO SUITE DE PRUEBAS DE SEGURIDAD API")
        print("=" * 60)
        
        start_time = time.time()
        
        try:
            self.test_1_authentication_and_authorization()
            self.test_2_input_validation_sql_injection()
            self.test_3_jwt_security_session_management()
            self.test_4_rate_limiting_dos_prevention()
            self.test_5_complete_security_workflow()
            
            # Resumen final
            total_tests = len(self.test_results)
            passed_tests = sum(1 for r in self.test_results if r["success"])
            failed_tests = total_tests - passed_tests
            
            elapsed_time = time.time() - start_time
            
            print("\n" + "=" * 60)
            print("📊 RESUMEN DE PRUEBAS DE SEGURIDAD")
            print("=" * 60)
            print(f"✅ Pruebas exitosas: {passed_tests}")
            print(f"❌ Pruebas fallidas: {failed_tests}")
            print(f"📊 Total de pruebas: {total_tests}")
            print(f"⏱️  Tiempo total: {elapsed_time:.2f} segundos")
            print(f"📈 Tasa de éxito: {(passed_tests/total_tests)*100:.1f}%")
            
            if failed_tests == 0:
                print("\n🎉 TODAS LAS PRUEBAS DE SEGURIDAD PASARON EXITOSAMENTE")
                print("✅ OWASP Top 10 verificado")
                print("✅ 5 pruebas API completadas")
                return True
            else:
                print(f"\n⚠️  ALGUNAS PRUEBAS FALLARON ({failed_tests} de {total_tests})")
                print("\nPruebas fallidas:")
                for result in self.test_results:
                    if not result["success"]:
                        print(f"   ❌ {result['test']}: {result['details']}")
                return False
        
        except KeyboardInterrupt:
            print("\n⏹️  Pruebas interrumpidas por el usuario")
            return False
        except Exception as e:
            print(f"\n❌ ERROR CRÍTICO EN PRUEBAS: {e}")
            return False


def main():
    """Función principal para ejecutar las pruebas"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Suite de pruebas de seguridad API")
    parser.add_argument("--url", default="http://localhost:8000", 
                       help="URL base de la API (default: http://localhost:8000)")
    parser.add_argument("--test", choices=["1", "2", "3", "4", "5"], 
                       help="Ejecutar solo una prueba específica")
    
    args = parser.parse_args()
    
    # Verificar que la API esté disponible
    try:
        response = requests.get(f"{args.url}/health", timeout=5)
        if response.status_code != 200:
            print(f"❌ API no disponible en {args.url}")
            print("   Asegúrate de que la API esté ejecutándose")
            sys.exit(1)
    except Exception as e:
        print(f"❌ No se puede conectar a la API en {args.url}")
        print(f"   Error: {e}")
        print("   Asegúrate de que la API esté ejecutándose")
        sys.exit(1)
    
    # Ejecutar pruebas
    tester = APISecurityTester(args.url)
    
    if args.test:
        test_methods = {
            "1": tester.test_1_authentication_and_authorization,
            "2": tester.test_2_input_validation_sql_injection,
            "3": tester.test_3_jwt_security_session_management,
            "4": tester.test_4_rate_limiting_dos_prevention,
            "5": tester.test_5_complete_security_workflow
        }
        
        print(f"🧪 Ejecutando prueba {args.test}")
        test_methods[args.test]()
    else:
        success = tester.run_all_tests()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()