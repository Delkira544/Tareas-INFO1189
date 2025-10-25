"""
Software Integrity Checker (OWASP A08)
Verificador de integridad de archivos críticos del sistema
"""
import hashlib
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime


class IntegrityChecker:
    """Verificador de integridad de archivos críticos"""
    
    def __init__(self, checksums_file: str = "integrity_checksums.json"):
        """
        Inicializar verificador de integridad
        
        Args:
            checksums_file: Archivo donde guardar los checksums
        """
        self.checksums_file = checksums_file
        
        # Archivos críticos a monitorear
        self.critical_files = [
            "main.py",
            "infrastructure/auth_service.py",
            "infrastructure/database.py",
            "infrastructure/security_config.py",
            "infrastructure/security_service.py",
            "infrastructure/security_logger.py",
            "presentation/middlewares/auth.py",
            "presentation/middlewares/rolemiddleware.py",
            "presentation/middlewares/security_headers.py"
        ]
        
        # Extensiones de archivos a verificar
        self.monitored_extensions = [".py", ".json", ".yaml", ".yml", ".toml", ".ini"]
    
    def calculate_file_checksum(self, file_path: str) -> Optional[str]:
        """
        Calcular checksum SHA-256 de un archivo
        
        Args:
            file_path: Ruta del archivo
            
        Returns:
            Checksum SHA-256 o None si el archivo no existe
        """
        try:
            if not Path(file_path).exists():
                return None
            
            with open(file_path, 'rb') as f:
                file_hash = hashlib.sha256()
                # Leer archivo en chunks para archivos grandes
                for chunk in iter(lambda: f.read(4096), b""):
                    file_hash.update(chunk)
                return file_hash.hexdigest()
        
        except (IOError, OSError) as e:
            print(f"⚠️  Error leyendo archivo {file_path}: {e}")
            return None
    
    def calculate_directory_checksums(self, directory: str) -> Dict[str, str]:
        """
        Calcular checksums de todos los archivos en un directorio
        
        Args:
            directory: Directorio a escanear
            
        Returns:
            Diccionario con rutas y checksums
        """
        checksums = {}
        
        try:
            for root, dirs, files in os.walk(directory):
                # Ignorar directorios __pycache__ y .git
                dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', '.pytest_cache', 'venv', '.venv']]
                
                for file in files:
                    file_path = Path(root) / file
                    
                    # Solo procesar archivos con extensiones monitoreadas
                    if file_path.suffix in self.monitored_extensions:
                        relative_path = str(file_path.relative_to(Path.cwd()))
                        checksum = self.calculate_file_checksum(str(file_path))
                        
                        if checksum:
                            checksums[relative_path] = checksum
        
        except Exception as e:
            print(f"⚠️  Error escaneando directorio {directory}: {e}")
        
        return checksums
    
    def generate_checksums(self) -> Dict[str, str]:
        """
        Generar checksums de archivos críticos
        
        Returns:
            Diccionario con checksums de archivos críticos
        """
        checksums = {}
        
        # Checksums de archivos críticos específicos
        for file_path in self.critical_files:
            checksum = self.calculate_file_checksum(file_path)
            if checksum:
                checksums[file_path] = checksum
            else:
                print(f"⚠️  Archivo crítico no encontrado: {file_path}")
        
        # Checksums de todo el directorio src
        if Path("src").exists():
            src_checksums = self.calculate_directory_checksums("src")
            checksums.update(src_checksums)
        
        return checksums
    
    def save_checksums(self, checksums: Optional[Dict[str, str]] = None) -> bool:
        """
        Guardar checksums en archivo
        
        Args:
            checksums: Checksums a guardar. Si None, se generan automáticamente
            
        Returns:
            True si se guardaron correctamente
        """
        try:
            if checksums is None:
                checksums = self.generate_checksums()
            
            checksum_data = {
                "generated_at": datetime.utcnow().isoformat(),
                "application": "products-api",
                "version": "2.0.0",
                "total_files": len(checksums),
                "checksums": checksums
            }
            
            with open(self.checksums_file, 'w') as f:
                json.dump(checksum_data, f, indent=2, sort_keys=True)
            
            print(f"✅ Checksums guardados: {len(checksums)} archivos en {self.checksums_file}")
            return True
        
        except Exception as e:
            print(f"❌ Error guardando checksums: {e}")
            return False
    
    def load_checksums(self) -> Optional[Dict[str, str]]:
        """
        Cargar checksums desde archivo
        
        Returns:
            Checksums cargados o None si hay error
        """
        try:
            if not Path(self.checksums_file).exists():
                return None
            
            with open(self.checksums_file, 'r') as f:
                data = json.load(f)
            
            return data.get("checksums", {})
        
        except Exception as e:
            print(f"❌ Error cargando checksums: {e}")
            return None
    
    def verify_integrity(self) -> Tuple[bool, List[str], List[str]]:
        """
        Verificar integridad de archivos críticos
        
        Returns:
            Tupla con (integridad_ok, archivos_modificados, archivos_nuevos)
        """
        stored_checksums = self.load_checksums()
        
        if stored_checksums is None:
            print("⚠️  No hay checksums almacenados. Generando baseline...")
            self.save_checksums()
            return True, [], []
        
        current_checksums = self.generate_checksums()
        
        modified_files = []
        new_files = []
        
        # Verificar archivos modificados
        for file_path, stored_checksum in stored_checksums.items():
            current_checksum = current_checksums.get(file_path)
            
            if current_checksum is None:
                print(f"⚠️  Archivo eliminado: {file_path}")
                modified_files.append(f"DELETED: {file_path}")
            
            elif current_checksum != stored_checksum:
                print(f"⚠️  Archivo modificado: {file_path}")
                modified_files.append(f"MODIFIED: {file_path}")
        
        # Verificar archivos nuevos
        for file_path in current_checksums:
            if file_path not in stored_checksums:
                print(f"ℹ️  Archivo nuevo detectado: {file_path}")
                new_files.append(f"NEW: {file_path}")
        
        integrity_ok = len(modified_files) == 0
        
        if integrity_ok:
            print("✅ Integridad de archivos verificada correctamente")
        else:
            print(f"⚠️  Integridad comprometida: {len(modified_files)} archivos modificados")
        
        return integrity_ok, modified_files, new_files
    
    def update_baseline(self) -> bool:
        """
        Actualizar baseline de checksums con el estado actual
        
        Returns:
            True si se actualizó correctamente
        """
        print("🔄 Actualizando baseline de integridad...")
        return self.save_checksums()
    
    def get_integrity_report(self) -> Dict[str, Any]:
        """
        Obtener reporte completo de integridad
        
        Returns:
            Reporte de integridad
        """
        integrity_ok, modified_files, new_files = self.verify_integrity()
        
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "integrity_status": "OK" if integrity_ok else "COMPROMISED",
            "total_critical_files": len(self.critical_files),
            "monitored_files": len(self.generate_checksums()),
            "modified_files": modified_files,
            "new_files": new_files,
            "checksums_file": self.checksums_file,
            "last_baseline": None
        }
        
        # Obtener fecha del último baseline
        try:
            with open(self.checksums_file, 'r') as f:
                data = json.load(f)
                report["last_baseline"] = data.get("generated_at")
        except:
            pass
        
        return report
    
    def monitor_file_changes(self, file_path: str) -> Dict[str, Any]:
        """
        Monitorear cambios en un archivo específico
        
        Args:
            file_path: Archivo a monitorear
            
        Returns:
            Información de cambios
        """
        stored_checksums = self.load_checksums()
        current_checksum = self.calculate_file_checksum(file_path)
        
        if not current_checksum:
            return {
                "file": file_path,
                "status": "NOT_FOUND",
                "message": "Archivo no encontrado"
            }
        
        if not stored_checksums or file_path not in stored_checksums:
            return {
                "file": file_path,
                "status": "NEW",
                "current_checksum": current_checksum,
                "message": "Archivo no estaba en el baseline"
            }
        
        stored_checksum = stored_checksums[file_path]
        
        if current_checksum == stored_checksum:
            return {
                "file": file_path,
                "status": "UNCHANGED",
                "checksum": current_checksum,
                "message": "Archivo sin cambios"
            }
        else:
            return {
                "file": file_path,
                "status": "MODIFIED",
                "stored_checksum": stored_checksum,
                "current_checksum": current_checksum,
                "message": "Archivo modificado detectado"
            }


# Instancia global del verificador de integridad
integrity_checker = IntegrityChecker()


def get_integrity_checker() -> IntegrityChecker:
    """Obtener instancia del verificador de integridad"""
    return integrity_checker