# azure_worker.py

import time
from PyQt6.QtCore import QThread, pyqtSignal
import azure.cognitiveservices.speech as speechsdk
from traductor_azure.src.config import AUDIO_CONFIG
from traductor_azure.src.logger import logger, log_performance, log_error_with_context

class WorkerStreaming(QThread):
    subtitulos_actualizados = pyqtSignal(str, object, bool)  # Cambiado para manejar múltiples traducciones
    estado_actualizado = pyqtSignal(str)

    def __init__(self, source_language, target_languages):
        super().__init__()
        self.source_language = source_language
        # Aceptar tanto un solo idioma como una lista
        if isinstance(target_languages, list):
            self.target_languages = [lang.split('-')[0] for lang in target_languages]
        else:
            self.target_languages = [target_languages.split('-')[0]]
        self.translation_recognizer = None
        # --- CAMBIO 1: Añadimos una bandera para controlar el bucle ---
        self.is_running = True

    def run(self):
        start_time = time.time()
        try:
            logger.info("Starting Azure worker", 
                       source_language=self.source_language, 
                       target_languages=self.target_languages)
            
            # Importar las credenciales actuales cada vez que se ejecute
            from traductor_azure.src.config import AZURE_SPEECH_KEY, AZURE_SPEECH_REGION, AUDIO_CONFIG
            translation_config = speechsdk.translation.SpeechTranslationConfig(
                subscription=AZURE_SPEECH_KEY,
                region=AZURE_SPEECH_REGION,
                speech_recognition_language=self.source_language,
            )
            
            # Configurar propiedades de audio para captura omnidireccional
            self._configure_audio_properties(translation_config)
            
            # Agregar todos los idiomas de destino
            for target_lang in self.target_languages:
                translation_config.add_target_language(target_lang)
            
            # Crear configuración de audio optimizada
            audio_config = self._create_optimized_audio_config()
            
            self.translation_recognizer = speechsdk.translation.TranslationRecognizer(
                translation_config=translation_config, audio_config=audio_config)

            # Conectamos las señales (eventos) antes de iniciar
            self.translation_recognizer.recognizing.connect(self.on_recognizing)
            self.translation_recognizer.recognized.connect(self.on_recognized)
            self.translation_recognizer.canceled.connect(self.on_canceled)
            self.translation_recognizer.session_started.connect(self._on_session_started)
            self.translation_recognizer.session_stopped.connect(self._on_session_stopped)

            # Iniciamos el reconocimiento de forma ASÍNCRONA
            self.translation_recognizer.start_continuous_recognition_async()

            # Mantenemos el hilo vivo con un bucle optimizado
            while self.is_running:
                time.sleep(0.1)

        except Exception as e:
            log_error_with_context(e, "Azure worker initialization")
            self.estado_actualizado.emit(f"❌ Error al iniciar Azure: {e}")
        finally:
            duration = (time.time() - start_time) * 1000
            log_performance("azure_worker_run", duration)
    
    def _on_session_started(self, evt):
        """Maneja el evento de inicio de sesión"""
        logger.info("Azure session started")
        self.estado_actualizado.emit("✅ Conectado a Azure. Habla ahora.")
    
    def _on_session_stopped(self, evt):
        """Maneja el evento de parada de sesión"""
        logger.info("Azure session stopped", reason=str(evt))
            
    def on_recognizing(self, event: speechsdk.translation.TranslationRecognitionEventArgs):
        start_time = time.time()
        try:
            original_text = event.result.text
            if not original_text:
                return
                
            # Obtener todas las traducciones disponibles
            traducciones = {}
            for target_lang in self.target_languages:
                translated_text = event.result.translations.get(target_lang)
                if translated_text:
                    traducciones[target_lang] = translated_text
            
            if traducciones:
                # Log de traducción en progreso
                logger.debug("Translation recognizing", 
                           original_length=len(original_text),
                           num_translations=len(traducciones))
                
                # Si hay múltiples idiomas, enviar diccionario
                if len(traducciones) > 1:
                    self.subtitulos_actualizados.emit(original_text, traducciones, False)
                else:
                    # Si solo hay uno, enviar el texto directamente para compatibilidad
                    self.subtitulos_actualizados.emit(original_text, list(traducciones.values())[0], False)
        except Exception as e:
            log_error_with_context(e, "Translation recognizing")
        finally:
            duration = (time.time() - start_time) * 1000
            if duration > 10:  # Solo log si toma más de 10ms
                log_performance("translation_recognizing", duration)

    def on_recognized(self, event: speechsdk.translation.TranslationRecognitionEventArgs):
        start_time = time.time()
        try:
            original_text = event.result.text
            if not original_text:
                return
                
            # Obtener todas las traducciones disponibles
            traducciones = {}
            for target_lang in self.target_languages:
                translated_text = event.result.translations.get(target_lang)
                if translated_text:
                    traducciones[target_lang] = translated_text
            
            if traducciones:
                # Log de traducción completada
                logger.log_translation(
                    original_text, 
                    list(traducciones.values())[0] if len(traducciones) == 1 else str(traducciones),
                    (time.time() - start_time) * 1000,
                    self.source_language,
                    self.target_languages[0] if len(self.target_languages) == 1 else str(self.target_languages)
                )
                
                # Si hay múltiples idiomas, enviar diccionario
                if len(traducciones) > 1:
                    self.subtitulos_actualizados.emit(original_text, traducciones, True)
                else:
                    # Si solo hay uno, enviar el texto directamente para compatibilidad
                    self.subtitulos_actualizados.emit(original_text, list(traducciones.values())[0], True)
        except Exception as e:
            log_error_with_context(e, "Translation recognized")
        finally:
            duration = (time.time() - start_time) * 1000
            log_performance("translation_recognized", duration)

    def on_canceled(self, event: speechsdk.translation.TranslationRecognitionCanceledEventArgs):
        logger.warning("Azure recognition canceled", reason=str(event.reason))
        
        if event.reason == speechsdk.CancellationReason.Error:
            error_details = event.error_details.lower()
            logger.log_azure_error("CANCELLATION_ERROR", event.error_details)
            
            # Manejo específico de errores comunes
            if "quota exceeded" in error_details or "error code: 1007" in error_details:
                error_msg = (
                    "❌ CUOTA EXCEDIDA: Has alcanzado el límite gratuito de Azure Speech Services.\n"
                    "💡 Soluciones:\n"
                    "• Espera hasta el próximo ciclo de facturación\n"
                    "• Crea una nueva cuenta de Azure gratuita\n"
                    "• Actualiza a plan de pago en portal.azure.com"
                )
                self.estado_actualizado.emit(error_msg)
            elif "unauthorized" in error_details or "401" in error_details:
                error_msg = (
                    "❌ CREDENCIALES INVÁLIDAS: Verifica tu Azure Speech Key y Region.\n"
                    "💡 Ve a Configuración (⚙️) para actualizar las credenciales."
                )
                self.estado_actualizado.emit(error_msg)
            elif "network" in error_details or "connection" in error_details:
                error_msg = (
                    "❌ ERROR DE CONEXIÓN: Verifica tu conexión a internet.\n"
                    "💡 Intenta nuevamente en unos momentos."
                )
                self.estado_actualizado.emit(error_msg)
            else:
                error_msg = f"❌ Error de Azure: {event.error_details}"
                self.estado_actualizado.emit(error_msg)

    def stop(self):
        logger.info("Stopping Azure worker")
        try:
            if self.translation_recognizer:
                # Detenemos el reconocimiento asíncronamente
                future = self.translation_recognizer.stop_continuous_recognition_async()
                future.get() # Esperamos a que la detención se complete
                logger.info("Azure recognition stopped successfully")
        except Exception as e:
            log_error_with_context(e, "Azure worker stop")
        finally:
            # Le decimos a nuestro bucle en run() que termine
            self.is_running = False

    def _configure_audio_properties(self, translation_config):
        """Configura las propiedades de audio para mejorar la captura omnidireccional"""
        try:
            # Configurar timeout de silencio para mejor detección
            translation_config.set_property(
                speechsdk.PropertyId.Speech_SegmentationSilenceTimeoutMs, 
                str(AUDIO_CONFIG["segmentation_silence_timeout"])
            )
            
            # Configurar tiempo máximo de segmentación
            translation_config.set_property(
                speechsdk.PropertyId.Speech_SegmentationMaximumTimeMs, 
                str(AUDIO_CONFIG["segmentation_max_time"])
            )
            
            # Habilitar logging de audio si está configurado
            if AUDIO_CONFIG["enable_audio_logging"]:
                translation_config.enable_audio_logging()
            
            # Configurar filtro de profanidad
            if AUDIO_CONFIG["profanity_filter"] == "masked":
                translation_config.set_profanity(speechsdk.ProfanityOption.Masked)
            elif AUDIO_CONFIG["profanity_filter"] == "removed":
                translation_config.set_profanity(speechsdk.ProfanityOption.Removed)
            else:
                translation_config.set_profanity(speechsdk.ProfanityOption.Raw)
            
            print("✅ Propiedades de audio configuradas para captura omnidireccional")
            
        except Exception as e:
            print(f"⚠️ Advertencia al configurar propiedades de audio: {e}")

    def _create_optimized_audio_config(self):
        """Crea una configuración de audio optimizada para captura omnidireccional"""
        try:
            # Crear configuración básica de audio
            audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
            
            # Configurar opciones de procesamiento de audio
            if AUDIO_CONFIG["enable_audio_processing"]:
                # Configurar supresión de ruido
                if AUDIO_CONFIG["noise_suppression"] == "moderate":
                    audio_config.set_property_by_name("SpeechServiceConnection_EnableNoiseSuppression", "true")
                elif AUDIO_CONFIG["noise_suppression"] == "aggressive":
                    audio_config.set_property_by_name("SpeechServiceConnection_EnableNoiseSuppression", "true")
                    audio_config.set_property_by_name("SpeechServiceConnection_NoiseSuppressionLevel", "high")
                
                # Configurar cancelación de eco
                if AUDIO_CONFIG["echo_cancellation"]:
                    audio_config.set_property_by_name("SpeechServiceConnection_EnableEchoCancellation", "true")
                
                # Configurar control automático de ganancia
                if AUDIO_CONFIG["auto_gain_control"]:
                    audio_config.set_property_by_name("SpeechServiceConnection_EnableAutoGainControl", "true")
            
            # Configurar sensibilidad del micrófono
            if AUDIO_CONFIG["microphone_sensitivity"] == "high":
                audio_config.set_property_by_name("SpeechServiceConnection_MicrophoneSensitivity", "high")
            elif AUDIO_CONFIG["microphone_sensitivity"] == "medium":
                audio_config.set_property_by_name("SpeechServiceConnection_MicrophoneSensitivity", "medium")
            else:
                audio_config.set_property_by_name("SpeechServiceConnection_MicrophoneSensitivity", "low")
            
            # Configurar boost de audio
            if AUDIO_CONFIG["audio_boost"]:
                audio_config.set_property_by_name("SpeechServiceConnection_EnableAudioBoost", "true")
            
            print("✅ Configuración de audio optimizada para captura omnidireccional")
            return audio_config
            
        except Exception as e:
            print(f"⚠️ Advertencia al crear configuración de audio: {e}")
            # Retornar configuración básica en caso de error
            return speechsdk.audio.AudioConfig(use_default_microphone=True)