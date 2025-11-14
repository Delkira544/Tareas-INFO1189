"""
Ejecutor de todos los tests OWASP A01, A03, A09
"""
import sys
import subprocess
import argparse


def run_test_file(test_file, url):
    """Ejecutar un archivo de test específico"""
    try:
        result = subprocess.run([sys.executable, test_file, "--url", url],
                                capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)


def main():
    parser = argparse.ArgumentParser(
        description="Ejecutar todos los tests OWASP")
    parser.add_argument("--url", default="http://localhost:8000",
                        help="URL de la API")
    parser.add_argument("--test", choices=["A01", "A03", "A09"],
                        help="Ejecutar solo un test específico")

    args = parser.parse_args()

    test_files = {
        "A01": "01_owasp.py",
        "A03": "03_owasp.py",
        "A09": "09_owasp.py"
    }

    if args.test:
        # Ejecutar solo un test específico
        test_files = {args.test: test_files[args.test]}

    print("🛡️  EJECUTANDO TESTS OWASP SIMPLIFICADOS")
    print("=" * 60)

    results = {}

    for test_name, test_file in test_files.items():
        print(f"\n🔍 Ejecutando {test_name}...")
        success, stdout, stderr = run_test_file(test_file, args.url)

        results[test_name] = success
        print(stdout)

        if stderr:
            print(f"Errores en {test_name}:")
            print(stderr)

    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN FINAL DE TESTS OWASP")
    print("=" * 60)

    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name}: {status}")

    total_passed = sum(results.values())
    total_tests = len(results)

    print(f"\nTotal: {total_passed}/{total_tests} categorías pasaron")

    if total_passed == total_tests:
        print("🎉 TODOS LOS TESTS OWASP PASARON!")
        return True
    else:
        print("⚠️  ALGUNOS TESTS FALLARON - Revisar vulnerabilidades")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
