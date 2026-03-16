# config.py

import json
import os
import time
from typing import Dict, Any, Optional

# --- Credenciales de Azure ---
# Valores por defecto - se pueden cambiar dinámicamente desde la UI
DEFAULT_AZURE_SPEECH_KEY = "CsDF058L2WuJ7VK0cJjpX1FPzVMOyS8NgF0YkvUp5YYpjYxEPY9uJQQJ99BHACYeBjFXJ3w3AAAYACOGxtgl"
DEFAULT_AZURE_SPEECH_REGION = "eastus"

# Archivo de configuración
CONFIG_FILE = "nexovoz_config.json"

# Variables dinámicas que se pueden cambiar desde la UI
AZURE_SPEECH_KEY = DEFAULT_AZURE_SPEECH_KEY
AZURE_SPEECH_REGION = DEFAULT_AZURE_SPEECH_REGION


class ConfigCache:
    """Caché para configuraciones de Azure con invalidación automática"""
    
    _azure_config = None
    _last_updated = None
    _cache_duration = 300  # 5 minutos
    
    @classmethod
    def get_azure_config(cls) -> Dict[str, str]:
        """Obtiene la configuración de Azure desde caché o la recarga si es necesario"""
        if cls._azure_config is None or cls._is_stale():
            cls._refresh_config()
        return cls._azure_config
    
    @classmethod
    def _is_stale(cls) -> bool:
        """Verifica si el caché está obsoleto"""
        if cls._last_updated is None:
            return True
        return time.time() - cls._last_updated > cls._cache_duration
    
    @classmethod
    def _refresh_config(cls):
        """Refresca la configuración desde el archivo"""
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    cls._azure_config = {
                        'key': config.get('azure_speech_key', DEFAULT_AZURE_SPEECH_KEY),
                        'region': config.get('azure_speech_region', DEFAULT_AZURE_SPEECH_REGION)
                    }
            else:
                cls._azure_config = {
                    'key': DEFAULT_AZURE_SPEECH_KEY,
                    'region': DEFAULT_AZURE_SPEECH_REGION
                }
            cls._last_updated = time.time()
        except Exception as e:
            print(f"⚠️ Error al cargar configuración: {e}")
            cls._azure_config = {
                'key': DEFAULT_AZURE_SPEECH_KEY,
                'region': DEFAULT_AZURE_SPEECH_REGION
            }
            cls._last_updated = time.time()
    
    @classmethod
    def invalidate_cache(cls):
        """Invalida el caché para forzar recarga"""
        cls._azure_config = None
        cls._last_updated = None

def load_config():
    """Carga la configuración desde el archivo usando caché optimizado"""
    global AZURE_SPEECH_KEY, AZURE_SPEECH_REGION, AUDIO_CONFIG
    
    # Usar caché para obtener configuración de Azure
    azure_config = ConfigCache.get_azure_config()
    AZURE_SPEECH_KEY = azure_config['key']
    AZURE_SPEECH_REGION = azure_config['region']
    
    # Cargar configuración de audio
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
                # Cargar configuración de audio si existe
                if 'audio_config' in config:
                    AUDIO_CONFIG.update(config['audio_config'])
                    print(f"✅ Configuración de audio cargada desde {CONFIG_FILE}")
                
                print(f"✅ Configuración cargada desde {CONFIG_FILE}")
        except Exception as e:
            print(f"❌ Error al cargar configuración de audio: {e}")
            print("🔄 Usando configuración de audio por defecto")
    else:
        print("📝 Archivo de configuración no encontrado, usando valores por defecto")

def save_config():
    """Guarda la configuración actual en el archivo"""
    try:
        config = {
            'azure_speech_key': AZURE_SPEECH_KEY,
            'azure_speech_region': AZURE_SPEECH_REGION,
            'audio_config': AUDIO_CONFIG
        }
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        print(f"✅ Configuración guardada en {CONFIG_FILE}")
        return True
    except Exception as e:
        print(f"❌ Error al guardar configuración: {e}")
        return False

def update_azure_credentials(key, region):
    """Actualiza las credenciales de Azure dinámicamente y las guarda"""
    global AZURE_SPEECH_KEY, AZURE_SPEECH_REGION
    AZURE_SPEECH_KEY = key
    AZURE_SPEECH_REGION = region
    
    # Invalidar caché para forzar recarga
    ConfigCache.invalidate_cache()
    
    save_config()  # Guardar automáticamente

def reset_to_default():
    """Restaura las credenciales por defecto y las guarda"""
    global AZURE_SPEECH_KEY, AZURE_SPEECH_REGION
    AZURE_SPEECH_KEY = DEFAULT_AZURE_SPEECH_KEY
    AZURE_SPEECH_REGION = DEFAULT_AZURE_SPEECH_REGION
    
    # Invalidar caché para forzar recarga
    ConfigCache.invalidate_cache()
    
    save_config()  # Guardar automáticamente

# --- Constantes de Audio ---
SAMPLE_RATE = 16000
CHUNK_SIZE = 1024

# --- Configuración de Audio para Captura Omnidireccional ---
# Configuraciones para mejorar la captura de audio desde todas las direcciones
AUDIO_CONFIG = {
    # Configuración básica de audio
    "sample_rate": 16000,
    "chunk_size": 1024,
    "channels": 1,  # Mono para mejor compatibilidad con Azure
    
    # Configuraciones para mejorar captura omnidireccional
    "enable_audio_processing": True,
    "noise_suppression": "moderate",  # moderate, aggressive, off
    "echo_cancellation": True,
    "auto_gain_control": True,
    
    # Configuraciones de sensibilidad
    "microphone_sensitivity": "high",  # low, medium, high
    "audio_boost": True,
    
    # Configuraciones de Azure Speech SDK
    "enable_audio_logging": False,
    "profanity_filter": "masked",  # raw, masked, removed
    "segmentation_silence_timeout": 500,  # ms
    "segmentation_max_time": 20000,  # ms
}

# Cargar configuración al importar el módulo
load_config()

# --- Diccionario de Idiomas para Azure ---
LANGUAGES = {
    "Español (España)": "es-ES",
    "Español (México)": "es-MX",
    "Inglés (EE.UU.)": "en-US",
    "Inglés (Reino Unido)": "en-GB",
    "Francés": "fr-FR",
    "Alemán": "de-DE",
    "Italiano": "it-IT",
    "Japonés": "ja-JP",
    "Portugués (Brasil)": "pt-BR",
    "Ruso": "ru-RU",
    "Chino (Mandarín)": "zh-CN"
}

# Azure usa el código completo para la traducción, así que el diccionario es el mismo.
TRANSLATE_CODES = LANGUAGES

# --- Configuración de MongoDB Atlas ---
MONGODB_CONNECTION_STRING = "mongodb+srv://admin:admin@traductor-1.d9gdxff.mongodb.net/?retryWrites=true&w=majority&appName=Traductor-1"
MONGODB_DATABASE_NAME = "Traductor"
MONGODB_COLLECTION_NAME = "Sesiones"