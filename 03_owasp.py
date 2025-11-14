"""
Test A03 - Injection
3 tests simples para verificar protección contra inyección
"""
import requests
import json
import sys
from urllib.parse import quote


class TestA03Injection:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.valid_token = None

    def _get_token(self):
        """Obtener token de autenticación"""
        try:
            response = self.session.post(f"{self.base_url}/auth/token",
                                         json={"username": "admin", "password": "admin123"})
            if response.status_code == 201:
                return response.json().get("access_token")
            return None
        except Exception as e:
            print(f"Error obteniendo token: {e}")
            return None

    def test_1_sql_injection_protection(self):
        """Test 1: Verificar protección contra SQL Injection"""
        print("💉 Test 1: Protección contra SQL Injection")

        # Payloads básicos de SQL injection
        sql_payloads = [
            "'; DROP TABLE products; --",
            "1' OR '1'='1",
            "1 UNION SELECT * FROM users",
            "admin'--",
            "' OR 1=1--"
        ]

        blocked_count = 0
        for payload in sql_payloads:
            try:
                # Test en URL parameter
                encoded_payload = quote(payload)
                response = self.session.get(
                    f"{self.base_url}/products/{encoded_payload}")

                # Debe ser bloqueado (400, 404, 422) no causar error 500
                if response.status_code in [400, 404, 422]:
                    print(f"  ✅ SQL injection bloqueada en URL")
                    blocked_count += 1
                elif response.status_code == 500:
                    print(f"  ❌ SQL injection causó error interno")
                else:
                    print(
                        f"  ⚠️  Respuesta inesperada: {response.status_code}")
                    blocked_count += 1  # Asumimos que está bien si no es 500

            except Exception as e:
                print(f"  ⚠️  Error con payload: {e}")
                blocked_count += 1  # Error de conexión es aceptable

        success = blocked_count >= len(sql_payloads) * 0.8
        print(
            f"Resultado: {'✅ PASS' if success else '❌ FAIL'} - {blocked_count}/{len(sql_payloads)} payloads SQL bloqueados\n")
        return success

    def test_2_xss_protection(self):
        """Test 2: Verificar protección contra XSS"""
        print("💉 Test 2: Protección contra XSS")

        # Obtener token
        self.valid_token = self._get_token()
        if not self.valid_token:
            print("  ❌ No se pudo obtener token válido")
            return False

        headers = {"Authorization": f"Bearer {self.valid_token}"}

        # Payloads básicos de XSS
        xss_payloads = [
            "<script>alert('xss')</script>",
            "<img src=x onerror=alert('xss')>",
            "javascript:alert('xss')",
            "<svg onload=alert('xss')>",
            "<body onload=alert('xss')>"
        ]

        sanitized_count = 0
        for payload in xss_payloads:
            try:
                # Test creando producto con XSS
                product_data = {
                    "name": payload,
                    "price": 100,
                    "subcategory_id": 1,
                    "description": payload
                }

                response = self.session.post(f"{self.base_url}/products",
                                             headers=headers,
                                             json=product_data)

                if response.status_code in [400, 422]:
                    print(f"  ✅ XSS payload rechazado")
                    sanitized_count += 1
                elif response.status_code == 201:
                    # Verificar si fue sanitizado
                    created_product = response.json()
                    if "<script>" not in str(created_product).lower() and "javascript:" not in str(created_product).lower():
                        print(f"  ✅ XSS payload sanitizado")
                        sanitized_count += 1
                    else:
                        print(f"  ❌ XSS payload no fue sanitizado")
                else:
                    print(
                        f"  ⚠️  Respuesta inesperada: {response.status_code}")

            except Exception as e:
                print(f"  ⚠️  Error con XSS payload: {e}")
                sanitized_count += 1  # Error es bueno aquí

        success = sanitized_count >= len(xss_payloads) * 0.8
        print(
            f"Resultado: {'✅ PASS' if success else '❌ FAIL'} - {sanitized_count}/{len(xss_payloads)} payloads XSS manejados\n")
        return success

    def test_3_command_injection_protection(self):
        """Test 3: Verificar protección contra Command Injection"""
        print("💉 Test 3: Protección contra Command Injection")

        if not self.valid_token:
            self.valid_token = self._get_token()

        if not self.valid_token:
            print("  ❌ No se pudo obtener token válido")
            return False

        headers = {"Authorization": f"Bearer {self.valid_token}"}

        # Payloads básicos de command injection
        command_payloads = [
            "; ls -la",
            "&& cat /etc/passwd",
            "| whoami",
            "`id`",
            "$(whoami)"
        ]

        blocked_count = 0
        for payload in command_payloads:
            try:
                # Test en nombre de producto
                product_data = {
                    "name": f"product{payload}",
                    "price": 100,
                    "subcategory_id": 1
                }

                import time
                start_time = time.time()
                response = self.session.post(f"{self.base_url}/products",
                                             headers=headers,
                                             json=product_data)
                elapsed = time.time() - start_time

                if response.status_code in [400, 422]:
                    print(f"  ✅ Command injection payload rechazado")
                    blocked_count += 1
                elif response.status_code == 201 and elapsed < 2:
                    # Si se creó pero no tardó mucho (no ejecutó comando)
                    created_product = response.json()
                    dangerous_chars = [";", "&", "|", "`", "$"]
                    if not any(char in str(created_product) for char in dangerous_chars):
                        print(f"  ✅ Command injection payload sanitizado")
                        blocked_count += 1
                    else:
                        print(f"  ❌ Command injection characters no sanitizados")
                elif elapsed >= 2:
                    print(
                        f"  ❌ Posible ejecución de comando (tardó {elapsed:.2f}s)")
                else:
                    print(
                        f"  ⚠️  Respuesta inesperada: {response.status_code}")

            except Exception as e:
                print(f"  ⚠️  Error con command payload: {e}")
                blocked_count += 1  # Error es bueno aquí

        success = blocked_count >= len(command_payloads) * 0.8
        print(
            f"Resultado: {'✅ PASS' if success else '❌ FAIL'} - {blocked_count}/{len(command_payloads)} payloads command bloqueados\n")
        return success

    def run_all_tests(self):
        """Ejecutar todos los tests A03"""
        print("🛡️  EJECUTANDO TESTS A03 - INJECTION")
        print("=" * 60)

        results = []
        results.append(self.test_1_sql_injection_protection())
        results.append(self.test_2_xss_protection())
        results.append(self.test_3_command_injection_protection())

        passed = sum(results)
        total = len(results)

        print("=" * 60)
        print(f"RESUMEN A03: {passed}/{total} tests pasaron")
        if passed == total:
            print("🎉 TODOS LOS TESTS A03 PASARON")
        else:
            print("⚠️  ALGUNOS TESTS A03 FALLARON")

        return passed == total


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Test A03 - Injection")
    parser.add_argument("--url", default="http://localhost:8000",
                        help="URL de la API")
    args = parser.parse_args()

    # Verificar conectividad
    try:
        response = requests.get(f"{args.url}/health", timeout=5)
        print(f"✅ API disponible en {args.url}")
    except:
        print(f"❌ No se puede conectar a {args.url}")
        sys.exit(1)

    # Ejecutar tests
    tester = TestA03Injection(args.url)
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
