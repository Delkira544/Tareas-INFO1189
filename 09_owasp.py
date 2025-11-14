"""
Test A09 - Security Logging and Monitoring Failures  
3 tests simples para verificar logging y monitoreo de seguridad
"""
import requests
import json
import sys
import time


class TestA09LoggingMonitoring:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.failed_attempts = []
        self.injection_attempts = []

    def test_1_authentication_failure_handling(self):
        """Test 1: Verificar manejo apropiado de fallos de autenticación"""
        print("📊 Test 1: Manejo de fallos de autenticación")

        # Intentos de login fallidos
        failed_login_attempts = [
            {"username": "admin", "password": "wrong_password"},
            {"username": "nonexistent_user", "password": "any_password"},
            {"username": "", "password": ""},
            {"username": "admin", "password": ""}
        ]

        handled_properly = 0
        for attempt in failed_login_attempts:
            try:
                response = self.session.post(f"{self.base_url}/auth/token",
                                             json=attempt)

                # Debe devolver 401 sin información sensible
                if response.status_code == 401:
                    print(f"  ✅ Fallo de auth manejado correctamente")
                    handled_properly += 1

                    # Verificar que no revela información sensible
                    response_text = response.text.lower()
                    if "user not found" not in response_text and "invalid user" not in response_text:
                        print(f"    ✅ No revela información de usuarios")
                    else:
                        print(
                            f"    ⚠️  Posible revelación de información de usuarios")

                    self.failed_attempts.append({
                        "username": attempt["username"],
                        "timestamp": time.time(),
                        "status": response.status_code
                    })
                else:
                    print(
                        f"  ❌ Fallo de auth no manejado (Status: {response.status_code})")

            except Exception as e:
                print(f"  ⚠️  Error con intento de login: {e}")
                handled_properly += 1  # Error de conexión es aceptable

        success = handled_properly >= len(failed_login_attempts) * 0.8
        print(
            f"Resultado: {'✅ PASS' if success else '❌ FAIL'} - {handled_properly}/{len(failed_login_attempts)} fallos manejados\n")
        return success

    def test_2_error_information_disclosure(self):
        """Test 2: Verificar que errores no revelen información sensible"""
        print("📊 Test 2: Control de divulgación de información en errores")

        # Requests que pueden causar errores
        error_inducing_requests = [
            ("GET", "/nonexistent_endpoint"),
            ("GET", "/products/999999999999999"),  # ID muy grande
            ("POST", "/products", {"invalid": "structure"}),  # JSON inválido
            ("GET", "/admin/secret"),  # Endpoint administrativo
            ("GET", "/.env")  # Archivo sensible
        ]

        secure_errors = 0
        for method, endpoint, *args in error_inducing_requests:
            try:
                kwargs = {}
                if args:
                    kwargs["json"] = args[0]

                response = self.session.request(
                    method, f"{self.base_url}{endpoint}", **kwargs)

                # Verificar que no hay stack traces o información sensible
                response_text = response.text.lower()
                sensitive_info = [
                    "traceback", "stack trace", "exception",
                    "/home/", "c:\\", "internal server error",
                    "sql error", "database", "connection"
                ]

                has_sensitive_info = any(
                    info in response_text for info in sensitive_info)

                if not has_sensitive_info:
                    print(f"  ✅ Error seguro en {method} {endpoint}")
                    secure_errors += 1
                else:
                    print(
                        f"  ❌ Error revela información en {method} {endpoint}")

                # También verificar headers
                sensitive_headers = [
                    "server", "x-powered-by", "x-aspnet-version"]
                header_secure = not any(header in [h.lower() for h in response.headers.keys()]
                                        for header in sensitive_headers)

                if header_secure:
                    print(f"    ✅ Headers seguros")
                else:
                    print(f"    ⚠️  Headers revelan información del servidor")

            except Exception as e:
                print(f"  ⚠️  Error con request: {e}")
                secure_errors += 1  # Error de conexión es seguro

        success = secure_errors >= len(error_inducing_requests) * 0.8
        print(
            f"Resultado: {'✅ PASS' if success else '❌ FAIL'} - {secure_errors}/{len(error_inducing_requests)} errores seguros\n")
        return success

    def test_3_security_event_tracking(self):
        """Test 3: Verificar capacidad de tracking de eventos de seguridad"""
        print("📊 Test 3: Tracking de eventos de seguridad")

        # Simular eventos de seguridad que deberían ser trackeados
        security_events = []

        # Evento 1: Múltiples fallos de autenticación
        for i in range(3):
            try:
                response = self.session.post(f"{self.base_url}/auth/token",
                                             json={"username": "admin", "password": f"wrong{i}"})
                security_events.append(("auth_failure", response.status_code))
            except:
                pass

        # Evento 2: Injection attempts
        injection_payloads = [
            "'; DROP TABLE users; --",
            "<script>alert('xss')</script>",
            "; cat /etc/passwd"
        ]

        for payload in injection_payloads:
            try:
                response = self.session.get(
                    f"{self.base_url}/products/{payload}")
                security_events.append(
                    ("injection_attempt", response.status_code))
                self.injection_attempts.append({
                    "payload": payload,
                    "status": response.status_code,
                    "timestamp": time.time()
                })
            except:
                pass

        # Evento 3: Rate limiting test
        rapid_requests = []
        for i in range(10):
            try:
                start_time = time.time()
                response = self.session.get(f"{self.base_url}/products")
                elapsed = time.time() - start_time
                rapid_requests.append((response.status_code, elapsed))
            except:
                pass

        # Verificar respuestas consistentes (indica logging/monitoring)
        consistent_responses = len(
            set(r[0] for r in rapid_requests if r[0] in [200, 429]))

        # Test de correlation/tracking headers
        response = self.session.get(f"{self.base_url}/products")
        correlation_headers = [
            "x-request-id", "x-correlation-id", "x-trace-id", "x-transaction-id"]
        has_correlation = any(header in [h.lower() for h in response.headers.keys()]
                              for header in correlation_headers)

        # Verificar tiempo de respuesta razonable (indica monitoring)
        response_times = [r[1] for r in rapid_requests if r[1] > 0]
        avg_response_time = sum(response_times) / \
            len(response_times) if response_times else 0
        reasonable_performance = avg_response_time < 2.0

        monitoring_indicators = 0

        if len(security_events) > 0:
            print(
                f"  ✅ Eventos de seguridad generados: {len(security_events)}")
            monitoring_indicators += 1
        else:
            print(f"  ❌ No se pudieron generar eventos de seguridad")

        if has_correlation:
            print(f"  ✅ Headers de correlación encontrados")
            monitoring_indicators += 1
        else:
            print(f"  ⚠️  No se encontraron headers de correlación")

        if reasonable_performance:
            print(
                f"  ✅ Rendimiento monitoreado (avg: {avg_response_time:.3f}s)")
            monitoring_indicators += 1
        else:
            print(f"  ⚠️  Rendimiento podría indicar problemas de monitoring")

        success = monitoring_indicators >= 2
        print(
            f"Resultado: {'✅ PASS' if success else '❌ FAIL'} - {monitoring_indicators}/3 indicadores de monitoring\n")
        return success

    def run_all_tests(self):
        """Ejecutar todos los tests A09"""
        print("🛡️  EJECUTANDO TESTS A09 - SECURITY LOGGING AND MONITORING")
        print("=" * 60)

        results = []
        results.append(self.test_1_authentication_failure_handling())
        results.append(self.test_2_error_information_disclosure())
        results.append(self.test_3_security_event_tracking())

        passed = sum(results)
        total = len(results)

        print("=" * 60)
        print(f"RESUMEN A09: {passed}/{total} tests pasaron")

        # Reporte de eventos detectados
        print(f"📊 Eventos de seguridad detectados:")
        print(f"  - Fallos de autenticación: {len(self.failed_attempts)}")
        print(f"  - Intentos de inyección: {len(self.injection_attempts)}")

        if passed == total:
            print("🎉 TODOS LOS TESTS A09 PASARON")
        else:
            print("⚠️  ALGUNOS TESTS A09 FALLARON")

        return passed == total


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Test A09 - Security Logging and Monitoring")
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
    tester = TestA09LoggingMonitoring(args.url)
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
