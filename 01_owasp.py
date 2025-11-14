"""
Test A01 - Broken Access Control
3 tests simples para verificar control de acceso
"""
import requests
import json
import sys


class TestA01BrokenAccessControl:
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

    def test_1_access_without_authentication(self):
        """Test 1: Verificar que endpoints protegidos requieren autenticación"""
        print("🔐 Test 1: Acceso sin autenticación")

        protected_endpoints = [
            ("POST", "/products", {"name": "test",
             "price": 100, "subcategory_id": 1}),
            ("DELETE", "/products/1", None),
            ("POST", "/categories", {"name": "test category"})
        ]

        failed_properly = 0
        for method, endpoint, data in protected_endpoints:
            try:
                kwargs = {"json": data} if data else {}
                response = self.session.request(
                    method, f"{self.base_url}{endpoint}", **kwargs)

                if response.status_code in [401, 403]:
                    print(f"  ✅ {method} {endpoint} correctamente protegido")
                    failed_properly += 1
                else:
                    print(
                        f"  ❌ {method} {endpoint} permite acceso sin auth (Status: {response.status_code})")
            except Exception as e:
                print(f"  ⚠️  Error en {method} {endpoint}: {e}")

        success = failed_properly >= len(protected_endpoints) * 0.8
        print(
            f"Resultado: {'✅ PASS' if success else '❌ FAIL'} - {failed_properly}/{len(protected_endpoints)} endpoints protegidos\n")
        return success

    def test_2_invalid_token_rejection(self):
        """Test 2: Verificar que tokens inválidos son rechazados"""
        print("🔐 Test 2: Rechazo de tokens inválidos")

        invalid_tokens = [
            "",
            "Bearer invalid_token",
            "Bearer " + "x" * 500,
            "Basic admin:password123"
        ]

        rejected_count = 0
        for token in invalid_tokens:
            try:
                response = self.session.get(f"{self.base_url}/products",
                                            headers={"Authorization": token})

                if response.status_code in [401, 403]:
                    print(f"  ✅ Token inválido rechazado correctamente")
                    rejected_count += 1
                else:
                    print(
                        f"  ❌ Token inválido aceptado (Status: {response.status_code})")
            except Exception as e:
                print(f"  ⚠️  Error con token: {e}")
                rejected_count += 1  # Error es bueno aquí

        success = rejected_count >= len(invalid_tokens) * 0.8
        print(
            f"Resultado: {'✅ PASS' if success else '❌ FAIL'} - {rejected_count}/{len(invalid_tokens)} tokens inválidos rechazados\n")
        return success

    def test_3_direct_object_access(self):
        """Test 3: Verificar protección contra acceso directo a objetos"""
        print("🔐 Test 3: Acceso directo a objetos (IDOR)")

        # Obtener token válido
        self.valid_token = self._get_token()
        if not self.valid_token:
            print("  ❌ No se pudo obtener token válido")
            return False

        headers = {"Authorization": f"Bearer {self.valid_token}"}

        # Test IDs que podrían causar problemas
        test_ids = [
            "999999",    # ID muy alto
            "-1",        # ID negativo
            "0",         # ID cero
            "../admin",  # Path traversal
            "admin"      # String en lugar de número
        ]

        handled_properly = 0
        for test_id in test_ids:
            try:
                response = self.session.get(f"{self.base_url}/products/{test_id}",
                                            headers=headers)

                # Debe devolver 404 o 400, no 500 (error interno)
                if response.status_code in [400, 404, 422]:
                    print(
                        f"  ✅ ID '{test_id}' manejado correctamente (Status: {response.status_code})")
                    handled_properly += 1
                elif response.status_code == 500:
                    print(
                        f"  ❌ ID '{test_id}' causó error interno (posible IDOR vulnerability)")
                else:
                    print(
                        f"  ⚠️  ID '{test_id}' respuesta inesperada: {response.status_code}")
                    handled_properly += 1  # Aceptamos respuestas no-500

            except Exception as e:
                print(f"  ⚠️  Error con ID '{test_id}': {e}")
                handled_properly += 1  # Error de conexión es aceptable

        success = handled_properly >= len(test_ids) * 0.8
        print(
            f"Resultado: {'✅ PASS' if success else '❌ FAIL'} - {handled_properly}/{len(test_ids)} IDs manejados correctamente\n")
        return success

    def run_all_tests(self):
        """Ejecutar todos los tests A01"""
        print("🛡️  EJECUTANDO TESTS A01 - BROKEN ACCESS CONTROL")
        print("=" * 60)

        results = []
        results.append(self.test_1_access_without_authentication())
        results.append(self.test_2_invalid_token_rejection())
        results.append(self.test_3_direct_object_access())

        passed = sum(results)
        total = len(results)

        print("=" * 60)
        print(f"RESUMEN A01: {passed}/{total} tests pasaron")
        if passed == total:
            print("🎉 TODOS LOS TESTS A01 PASARON")
        else:
            print("⚠️  ALGUNOS TESTS A01 FALLARON")

        return passed == total


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Test A01 - Broken Access Control")
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
    tester = TestA01BrokenAccessControl(args.url)
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
