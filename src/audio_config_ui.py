# audio_config_ui.py
# Interfaz para configurar opciones de audio para captura omnidireccional

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QComboBox, QCheckBox, QSpinBox, QGroupBox,
                            QPushButton, QMessageBox)
from PyQt6.QtCore import Qt
from traductor_azure.src.config import AUDIO_CONFIG
import json

class AudioConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuración de Audio - Captura Omnidireccional")
        self.setModal(True)
        self.resize(500, 600)
        
        self.audio_config = AUDIO_CONFIG.copy()
        self.setup_ui()
        self.load_current_config()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Grupo de configuración básica
        basic_group = QGroupBox("Configuración Básica")
        basic_layout = QVBoxLayout()
        
        # Sample Rate
        sample_rate_layout = QHBoxLayout()
        sample_rate_layout.addWidget(QLabel("Frecuencia de muestreo:"))
        self.sample_rate_combo = QComboBox()
        self.sample_rate_combo.addItems(["8000", "16000", "22050", "44100", "48000"])
        sample_rate_layout.addWidget(self.sample_rate_combo)
        basic_layout.addLayout(sample_rate_layout)
        
        # Chunk Size
        chunk_layout = QHBoxLayout()
        chunk_layout.addWidget(QLabel("Tamaño de chunk:"))
        self.chunk_size_spin = QSpinBox()
        self.chunk_size_spin.setRange(256, 4096)
        self.chunk_size_spin.setSingleStep(256)
        chunk_layout.addWidget(self.chunk_size_spin)
        basic_layout.addLayout(chunk_layout)
        
        basic_group.setLayout(basic_layout)
        layout.addWidget(basic_group)
        
        # Grupo de procesamiento de audio
        processing_group = QGroupBox("Procesamiento de Audio")
        processing_layout = QVBoxLayout()
        
        # Habilitar procesamiento de audio
        self.enable_processing = QCheckBox("Habilitar procesamiento de audio")
        processing_layout.addWidget(self.enable_processing)
        
        # Supresión de ruido
        noise_layout = QHBoxLayout()
        noise_layout.addWidget(QLabel("Supresión de ruido:"))
        self.noise_suppression = QComboBox()
        self.noise_suppression.addItems(["off", "moderate", "aggressive"])
        noise_layout.addWidget(self.noise_suppression)
        processing_layout.addLayout(noise_layout)
        
        # Cancelación de eco
        self.echo_cancellation = QCheckBox("Cancelación de eco")
        processing_layout.addWidget(self.echo_cancellation)
        
        # Control automático de ganancia
        self.auto_gain_control = QCheckBox("Control automático de ganancia")
        processing_layout.addWidget(self.auto_gain_control)
        
        processing_group.setLayout(processing_layout)
        layout.addWidget(processing_group)
        
        # Grupo de sensibilidad
        sensitivity_group = QGroupBox("Sensibilidad del Micrófono")
        sensitivity_layout = QVBoxLayout()
        
        # Sensibilidad del micrófono
        sens_layout = QHBoxLayout()
        sens_layout.addWidget(QLabel("Sensibilidad:"))
        self.microphone_sensitivity = QComboBox()
        self.microphone_sensitivity.addItems(["low", "medium", "high"])
        sens_layout.addWidget(self.microphone_sensitivity)
        sensitivity_layout.addLayout(sens_layout)
        
        # Boost de audio
        self.audio_boost = QCheckBox("Boost de audio")
        sensitivity_layout.addWidget(self.audio_boost)
        
        sensitivity_group.setLayout(sensitivity_layout)
        layout.addWidget(sensitivity_group)
        
        # Grupo de configuración de Azure
        azure_group = QGroupBox("Configuración de Azure Speech SDK")
        azure_layout = QVBoxLayout()
        
        # Timeout de silencio
        silence_layout = QHBoxLayout()
        silence_layout.addWidget(QLabel("Timeout de silencio (ms):"))
        self.silence_timeout = QSpinBox()
        self.silence_timeout.setRange(100, 5000)
        self.silence_timeout.setSingleStep(100)
        silence_layout.addWidget(self.silence_timeout)
        azure_layout.addLayout(silence_layout)
        
        # Tiempo máximo de segmentación
        max_time_layout = QHBoxLayout()
        max_time_layout.addWidget(QLabel("Tiempo máximo de segmentación (ms):"))
        self.max_time = QSpinBox()
        self.max_time.setRange(10000, 70000)
        self.max_time.setSingleStep(1000)
        max_time_layout.addWidget(self.max_time)
        azure_layout.addLayout(max_time_layout)
        
        # Filtro de profanidad
        profanity_layout = QHBoxLayout()
        profanity_layout.addWidget(QLabel("Filtro de profanidad:"))
        self.profanity_filter = QComboBox()
        self.profanity_filter.addItems(["raw", "masked", "removed"])
        profanity_layout.addWidget(self.profanity_filter)
        azure_layout.addLayout(profanity_layout)
        
        # Logging de audio
        self.audio_logging = QCheckBox("Habilitar logging de audio")
        azure_layout.addWidget(self.audio_logging)
        
        azure_group.setLayout(azure_layout)
        layout.addWidget(azure_group)
        
        # Botones
        button_layout = QHBoxLayout()
        
        self.reset_button = QPushButton("Restaurar por defecto")
        self.reset_button.clicked.connect(self.reset_to_default)
        button_layout.addWidget(self.reset_button)
        
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        self.save_button = QPushButton("Guardar")
        self.save_button.clicked.connect(self.save_config)
        button_layout.addWidget(self.save_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def load_current_config(self):
        """Carga la configuración actual"""
        self.sample_rate_combo.setCurrentText(str(self.audio_config["sample_rate"]))
        self.chunk_size_spin.setValue(self.audio_config["chunk_size"])
        self.enable_processing.setChecked(self.audio_config["enable_audio_processing"])
        self.noise_suppression.setCurrentText(self.audio_config["noise_suppression"])
        self.echo_cancellation.setChecked(self.audio_config["echo_cancellation"])
        self.auto_gain_control.setChecked(self.audio_config["auto_gain_control"])
        self.microphone_sensitivity.setCurrentText(self.audio_config["microphone_sensitivity"])
        self.audio_boost.setChecked(self.audio_config["audio_boost"])
        self.silence_timeout.setValue(self.audio_config["segmentation_silence_timeout"])
        self.max_time.setValue(self.audio_config["segmentation_max_time"])
        self.profanity_filter.setCurrentText(self.audio_config["profanity_filter"])
        self.audio_logging.setChecked(self.audio_config["enable_audio_logging"])
    
    def reset_to_default(self):
        """Restaura la configuración por defecto"""
        from traductor_azure.src.config import AUDIO_CONFIG
        self.audio_config = AUDIO_CONFIG.copy()
        self.load_current_config()
        QMessageBox.information(self, "Restaurado", "Configuración restaurada a valores por defecto.")
    
    def save_config(self):
        """Guarda la configuración actual"""
        try:
            # Actualizar configuración
            self.audio_config.update({
                "sample_rate": int(self.sample_rate_combo.currentText()),
                "chunk_size": self.chunk_size_spin.value(),
                "enable_audio_processing": self.enable_processing.isChecked(),
                "noise_suppression": self.noise_suppression.currentText(),
                "echo_cancellation": self.echo_cancellation.isChecked(),
                "auto_gain_control": self.auto_gain_control.isChecked(),
                "microphone_sensitivity": self.microphone_sensitivity.currentText(),
                "audio_boost": self.audio_boost.isChecked(),
                "segmentation_silence_timeout": self.silence_timeout.value(),
                "segmentation_max_time": self.max_time.value(),
                "profanity_filter": self.profanity_filter.currentText(),
                "enable_audio_logging": self.audio_logging.isChecked()
            })
            
            # Guardar en archivo de configuración
            from traductor_azure.src.config import AZURE_SPEECH_KEY, AZURE_SPEECH_REGION
            config_data = {
                "azure_speech_key": AZURE_SPEECH_KEY,
                "azure_speech_region": AZURE_SPEECH_REGION,
                "audio_config": self.audio_config
            }
            
            with open("nexovoz_config.json", 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=4, ensure_ascii=False)
            
            # Actualizar configuración global
            import traductor_azure.src.config as config
            config.AUDIO_CONFIG.update(self.audio_config)
            
            QMessageBox.information(self, "Guardado", "Configuración de audio guardada exitosamente.")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al guardar la configuración: {e}")
    
