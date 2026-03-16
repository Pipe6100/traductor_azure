# logger.py
# Sistema de logging estructurado para NexoVoz

import logging
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum

class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class StructuredLogger:
    """Logger estructurado para la aplicación NexoVoz"""
    
    def __init__(self, name: str = 'nexovoz', level: LogLevel = LogLevel.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.value))
        
        # Evitar duplicar handlers
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """Configura los handlers de logging"""
        # Handler para consola
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # Handler para archivo (opcional)
        if os.getenv('NEXOVOZ_LOG_FILE', 'false').lower() == 'true':
            file_handler = logging.FileHandler('nexovoz.log', encoding='utf-8')
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)
    
    def _log_structured(self, level: str, message: str, **kwargs):
        """Log estructurado con metadatos"""
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'message': message,
            **kwargs
        }
        
        if level == 'DEBUG':
            self.logger.debug(json.dumps(log_data, ensure_ascii=False))
        elif level == 'INFO':
            self.logger.info(json.dumps(log_data, ensure_ascii=False))
        elif level == 'WARNING':
            self.logger.warning(json.dumps(log_data, ensure_ascii=False))
        elif level == 'ERROR':
            self.logger.error(json.dumps(log_data, ensure_ascii=False))
        elif level == 'CRITICAL':
            self.logger.critical(json.dumps(log_data, ensure_ascii=False))
    
    def debug(self, message: str, **kwargs):
        """Log de debug"""
        self._log_structured('DEBUG', message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Log de información"""
        self._log_structured('INFO', message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log de advertencia"""
        self._log_structured('WARNING', message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log de error"""
        self._log_structured('ERROR', message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log crítico"""
        self._log_structured('CRITICAL', message, **kwargs)
    
    def log_translation(self, original: str, translated: str, duration_ms: float, 
                       source_lang: str, target_lang: str, **kwargs):
        """Log específico para traducciones"""
        self.info(
            "Translation completed",
            event_type="translation",
            original_length=len(original),
            translated_length=len(translated),
            duration_ms=duration_ms,
            source_language=source_lang,
            target_language=target_lang,
            **kwargs
        )
    
    def log_azure_error(self, error_code: str, error_details: str, **kwargs):
        """Log específico para errores de Azure"""
        self.error(
            "Azure Speech Service error",
            event_type="azure_error",
            error_code=error_code,
            error_details=error_details,
            **kwargs
        )
    
    def log_mongodb_operation(self, operation: str, success: bool, duration_ms: float, **kwargs):
        """Log específico para operaciones de MongoDB"""
        level = 'info' if success else 'error'
        self._log_structured(
            level,
            f"MongoDB {operation}",
            event_type="mongodb_operation",
            operation=operation,
            success=success,
            duration_ms=duration_ms,
            **kwargs
        )
    
    def log_ui_event(self, event_type: str, component: str, **kwargs):
        """Log específico para eventos de UI"""
        self.debug(
            f"UI event: {event_type}",
            event_type="ui_event",
            ui_event=event_type,
            component=component,
            **kwargs
        )

# Instancia global del logger
logger = StructuredLogger()

# Funciones de conveniencia
def log_performance(operation: str, duration_ms: float, **kwargs):
    """Log de rendimiento"""
    logger.info(
        f"Performance: {operation}",
        event_type="performance",
        operation=operation,
        duration_ms=duration_ms,
        **kwargs
    )

def log_error_with_context(error: Exception, context: str, **kwargs):
    """Log de error con contexto"""
    logger.error(
        f"Error in {context}: {str(error)}",
        event_type="error",
        context=context,
        error_type=type(error).__name__,
        error_message=str(error),
        **kwargs
    )
