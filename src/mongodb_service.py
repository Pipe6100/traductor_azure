# mongodb_service.py

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime
from traductor_azure.src.config import MONGODB_CONNECTION_STRING, MONGODB_DATABASE_NAME, MONGODB_COLLECTION_NAME
import threading
import time
from typing import Optional

class MongoDBConnectionPool:
    """Pool de conexiones singleton para MongoDB"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.client = None
            self.database = None
            self.collection = None
            self.is_connected = False
            self._connection_lock = threading.Lock()
            self._last_health_check = 0
            self._health_check_interval = 30  # 30 segundos
            self._initialized = True
    
    def get_connection(self):
        """Obtiene una conexión del pool"""
        with self._connection_lock:
            if not self.is_connected or self._is_connection_stale():
                self._connect()
            return self.client, self.database, self.collection
    
    def _is_connection_stale(self):
        """Verifica si la conexión está obsoleta"""
        return time.time() - self._last_health_check > self._health_check_interval
    
    def _connect(self):
        """Establece conexión con MongoDB Atlas"""
        try:
            if self.client:
                self.client.close()
            
            self.client = MongoClient(
                MONGODB_CONNECTION_STRING, 
                server_api=ServerApi('1'),
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
                socketTimeoutMS=5000,
                maxPoolSize=10,  # Pool de conexiones
                minPoolSize=1,
                maxIdleTimeMS=30000  # 30 segundos
            )
            self.database = self.client[MONGODB_DATABASE_NAME]
            self.collection = self.database[MONGODB_COLLECTION_NAME]
            
            # Verificar la conexión
            self.client.admin.command('ping')
            self.is_connected = True
            self._last_health_check = time.time()
            print("✅ Conexión MongoDB establecida con pool de conexiones")
            
        except Exception as e:
            print(f"❌ Error al conectar con MongoDB: {e}")
            self.is_connected = False
            raise
    
    def close(self):
        """Cierra todas las conexiones del pool"""
        with self._connection_lock:
            if self.client:
                self.client.close()
                self.is_connected = False
                print("🔌 Pool de conexiones MongoDB cerrado")

class MongoDBService:
    """Servicio optimizado para manejar operaciones con MongoDB Atlas"""
    
    def __init__(self):
        self.pool = MongoDBConnectionPool()
        self._retry_attempts = 3
        self._retry_delay = 1
        
    def connect(self):
        """Establece conexión con MongoDB Atlas usando pool"""
        try:
            self.pool.get_connection()
            return True
        except Exception as e:
            print(f"❌ Error al conectar con MongoDB: {e}")
            print("💡 Asegúrate de reemplazar <db_password> con tu contraseña real en config.py")
            return False
    
    def disconnect(self):
        """Cierra la conexión con MongoDB"""
        self.pool.close()
    
    def save_session(self, session_data, source_language, target_languages):
        """
        Guarda una sesión de traducción en MongoDB con retry automático
        
        Args:
            session_data: Lista de diccionarios con los datos de la sesión
            source_language: Idioma de origen
            target_languages: Lista de idiomas de destino
        """
        for attempt in range(self._retry_attempts):
            try:
                # Obtener conexión del pool
                client, database, collection = self.pool.get_connection()
                
                # Crear documento de sesión
                session_document = {
                    "fecha_creacion": datetime.now(),
                    "idioma_origen": source_language,
                    "idiomas_destino": target_languages,
                    "total_frases": len(session_data),
                    "frases": session_data,
                    "estado": "completada"
                }
                
                # Insertar en la colección
                result = collection.insert_one(session_document)
                
                if result.inserted_id:
                    print(f"✅ Sesión guardada en MongoDB con ID: {result.inserted_id}")
                    return True
                else:
                    print("❌ Error al insertar la sesión en MongoDB")
                    return False
                    
            except Exception as e:
                print(f"❌ Error al guardar sesión en MongoDB (intento {attempt + 1}): {e}")
                
                if attempt < self._retry_attempts - 1:
                    # Esperar antes del siguiente intento
                    time.sleep(self._retry_delay * (2 ** attempt))  # Backoff exponencial
                    # Invalidar conexión para forzar reconexión
                    self.pool._is_connected = False
                else:
                    print("❌ Falló después de todos los intentos")
                    return False
        
        return False
    

# Instancia global del servicio
mongodb_service = MongoDBService()
