from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QFrame,
    QGraphicsDropShadowEffect,
    QDialog,
    QLineEdit,
    QMessageBox,
    QCheckBox,
    QScrollArea,
    QSizePolicy,
)
from PyQt6.QtCore import (
    Qt,
    QThread,
    pyqtSignal,
    QTimer,
)
from PyQt6.QtGui import QFont, QColor

from traductor_azure.src.config import (
    LANGUAGES,
    TRANSLATE_CODES,
    AZURE_SPEECH_KEY,
    AZURE_SPEECH_REGION,
    update_azure_credentials,
    reset_to_default,
)
from traductor_azure.src.azure_worker import WorkerStreaming
from traductor_azure.src.mongodb_service import mongodb_service
from traductor_azure.src.audio_config_ui import AudioConfigDialog
from traductor_azure.src.styles import StyleManager


class DebouncedLabel(QLabel):
    """Label con debouncing para evitar actualizaciones excesivas"""
    
    def __init__(self, parent=None, delay=100):
        super().__init__(parent)
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self._update_text)
        self._pending_text = ""
        self._delay = delay
    
    def setTextDebounced(self, text, delay=None):
        """Establece el texto con debouncing"""
        self._pending_text = text
        self.timer.start(delay or self._delay)
    
    def _update_text(self):
        """Actualiza el texto después del delay"""
        if self._pending_text:
            self.setText(self._pending_text)
            self._pending_text = ""


class SaveWorker(QThread):
    """Worker para guardar sesión en MongoDB y localmente de forma asíncrona"""

    save_completed = pyqtSignal(bool, str)  # success, message

    def __init__(self, session_data, source_lang, target_langs, session_name):
        super().__init__()
        self.session_data = session_data
        self.source_lang = source_lang
        self.target_langs = target_langs
        self.session_name = session_name

    def run(self):
        """Ejecuta el guardado en MongoDB y localmente en un hilo separado"""
        try:
            # Guardar en MongoDB
            mongodb_success = mongodb_service.save_session(
                self.session_data, self.source_lang, self.target_langs
            )
            
            # Guardar localmente
            local_success = self._save_locally()

            # Determinar mensaje de resultado
            if mongodb_success and local_success:
                message = f"✅ Sesión guardada en MongoDB y localmente: {self.session_name}"
            elif mongodb_success and not local_success:
                message = f"✅ Sesión guardada en MongoDB (error local): {self.session_name}"
            elif not mongodb_success and local_success:
                message = f"✅ Sesión guardada localmente (error MongoDB): {self.session_name}"
            else:
                message = f"❌ Error al guardar en MongoDB y localmente: {self.session_name}"

            self.save_completed.emit(mongodb_success or local_success, message)

        except Exception as e:
            error_msg = f"❌ Error al guardar: {str(e)[:50]}..."
            self.save_completed.emit(False, error_msg)

    def _save_locally(self):
        """Guarda la sesión como archivos TXT en la carpeta de Descargas"""
        try:
            from pathlib import Path
            
            # Crear directorio en Descargas
            downloads_path = Path.home() / "Downloads"
            downloads_path.mkdir(exist_ok=True)
            nexovoz_path = downloads_path / "NexoVoz_Sesiones"
            nexovoz_path.mkdir(exist_ok=True)
            
            # Archivo principal con todas las traducciones
            session_file = nexovoz_path / f"{self.session_name}.txt"
            with open(session_file, 'w', encoding='utf-8') as f:
                f.write("=" * 60 + "\n")
                f.write(f"SESIÓN DE TRADUCCIÓN - {self.session_name}\n")
                f.write("=" * 60 + "\n")
                f.write(f"Idioma de origen: {self.source_lang}\n")
                f.write(f"Idiomas de destino: {', '.join(self.target_langs)}\n")
                f.write(f"Total de frases: {len(self.session_data)}\n")
                f.write(f"Fecha: {self.session_data[0]['timestamp'] if self.session_data else 'N/A'}\n")
                f.write("=" * 60 + "\n\n")
                
                for i, frase in enumerate(self.session_data, 1):
                    f.write(f"[{i}] {frase['timestamp']}\n")
                    f.write(f"Original: {frase['original']}\n")
                    if 'translations' in frase:
                        for idioma, traduccion in frase['translations'].items():
                            f.write(f"Traducción ({idioma}): {traduccion}\n")
                    else:
                        f.write(f"Traducción: {frase['translated']}\n")
                    f.write("-" * 40 + "\n\n")
            
            # Archivos separados por idioma si hay múltiples idiomas
            if self.target_langs and len(self.target_langs) > 1:
                for target_lang in self.target_langs:
                    lang_file = nexovoz_path / f"{self.session_name}_{target_lang}.txt"
                    with open(lang_file, 'w', encoding='utf-8') as f:
                        f.write(f"TRADUCCIONES EN {target_lang.upper()}\n")
                        f.write("=" * 40 + "\n\n")
                        for i, frase in enumerate(self.session_data, 1):
                            f.write(f"[{i}] {frase['timestamp']}\n")
                            f.write(f"Original: {frase['original']}\n")
                            if 'translations' in frase and target_lang in frase['translations']:
                                f.write(f"Traducción: {frase['translations'][target_lang]}\n")
                            elif 'translated' in frase:
                                f.write(f"Traducción: {frase['translated']}\n")
                            f.write("-" * 30 + "\n\n")
            
            print(f"✅ Archivos guardados localmente en: {nexovoz_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error al guardar localmente: {e}")
            return False


class ModernCard(QFrame):
    """Tarjeta moderna con sombra y estilo consistente"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Shape.NoFrame)
        self._apply_modern_style()

    def _apply_modern_style(self):
        """Aplica el estilo moderno a la tarjeta"""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)
        self.setStyleSheet(StyleManager.get_modern_card_style())


class VentanaFlotante(QWidget):
    PORCENTAJE_ANCHO = 0.90  # 85% del ancho de la pantalla

    def __init__(self):
        super().__init__()
        self._setup_window()
        self._setup_variables()
        self._setup_ui()
        self._calcular_y_establecer_ancho()

    def _setup_window(self):
        """Configura las propiedades de la ventana"""
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

    def _setup_variables(self):
        """Inicializa las variables de estado"""
        self.drag_position = None
        self.traducciones_activas = {}
        self.posicion_inicial_establecida = False

    def _setup_ui(self):
        """Configura la interfaz de usuario"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.label = DebouncedLabel("...", delay=50)  # Debouncing más rápido para subtítulos
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setMinimumHeight(40)
        self.label.setMouseTracking(True)
        self.label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

        font = QFont("Segoe UI", 30, QFont.Weight.Bold)
        self.label.setFont(font)

        self._aplicar_estilo_moderno()
        layout.addWidget(self.label)

    def _calcular_y_establecer_ancho(self):
        """Calcula el ancho basado en el 85% de la pantalla y lo establece"""
        try:
            # Obtener la pantalla principal
            screen = self.screen()
            if not screen:
                # Fallback si no hay pantalla disponible
                ancho_pantalla = 1920
            else:
                ancho_pantalla = screen.availableGeometry().width()

            # Calcular el 85% del ancho de la pantalla
            ancho_calculado = int(ancho_pantalla * self.PORCENTAJE_ANCHO)

            # Establecer el ancho fijo
            self.setFixedWidth(ancho_calculado)

            # Configurar el label con el ancho apropiado (menos padding)
            ancho_label = ancho_calculado - 70  # 35px padding cada lado
            self.label.setFixedWidth(ancho_label)

        except Exception as e:
            print(f"Error al calcular ancho: {e}")
            # Fallback a un ancho por defecto
            ancho_fallback = 950
            self.setFixedWidth(ancho_fallback)
            self.label.setFixedWidth(ancho_fallback - 70)

    def _aplicar_estilo_moderno(self):
        """Aplica el estilo moderno al label del globo"""
        self.label.setStyleSheet(StyleManager.get_globe_style())
        self.setMouseTracking(True)

    def _generar_html_subtitulos(self) -> str:
        """Genera el contenido HTML para el QLabel con límites de filas según el número de idiomas."""
        if not self.traducciones_activas:
            return ""

        # Filtrar idiomas activos de una vez (optimización)
        idiomas_activos = {
            idioma: texto for idioma, texto in self.traducciones_activas.items() 
            if texto.strip()
        }
        num_idiomas = len(idiomas_activos)

        if num_idiomas == 0:
            return ""

        # Pre-allocar lista para mejor rendimiento
        html_parts = []
        html_parts_append = html_parts.append  # Cache de método

        if num_idiomas == 1:
            # Un solo idioma: máximo 2 filas con efecto de scroll
            for idioma, texto in idiomas_activos.items():
                bandera = self._obtener_bandera_idioma(idioma)
                texto_escapado = self._escapar_html(texto.strip())

                # Dividir el texto en líneas para el efecto de scroll
                lineas = self._procesar_texto(
                    texto_escapado, max_lineas=2, modo="scroll"
                )

                # Crear HTML con las dos líneas usando f-strings optimizados
                p_style = "margin: 0; padding: 0; line-height: 1.2; white-space: nowrap; overflow: hidden;"
                for i, linea in enumerate(lineas[:2]):  # Máximo 2 líneas
                    if i == 0:
                        # Primera línea con bandera
                        html_parts_append(f"<p style='{p_style}'>{bandera} {linea}</p>")
                    else:
                        # Segunda línea sin bandera
                        html_parts_append(f"<p style='{p_style}'>{linea}</p>")

        else:
            # Múltiples idiomas: 1 fila por idioma con colores diferentes
            for i, (idioma, texto) in enumerate(idiomas_activos.items()):
                bandera = self._obtener_bandera_idioma(idioma)
                texto_escapado = self._escapar_html(texto.strip())

                # Aplicar efecto de scroll para múltiples idiomas
                texto_procesado = self._procesar_texto(
                    texto_escapado, max_lineas=1, modo="scroll"
                )

                # Asignar color según el orden del idioma
                color = self._obtener_color_idioma(i)

                # Estilo para 1 línea por idioma con color
                margin_bottom = " margin-bottom: 4px;" if i < num_idiomas - 1 else ""
                p_style = f"margin: 0; padding: 0;{margin_bottom} white-space: nowrap; overflow: hidden; color: {color};"
                texto_final = texto_procesado[0] if texto_procesado else ''
                html_parts_append(f"<p style='{p_style}'>{bandera} {texto_final}</p>")

        return "".join(html_parts)

    def _obtener_color_idioma(self, indice: int) -> str:
        """Obtiene el color para cada idioma según su orden"""
        # Usar tupla para mejor rendimiento (inmutable)
        colores = (
            "#FFFFFF",  # Primer idioma: blanco (por defecto)
            "#FFD700",  # Segundo idioma: amarillo dorado
            "#00FF7F",  # Tercer idioma: verde primavera
            "#FF6B6B",  # Cuarto idioma: rojo coral
            "#4ECDC4",  # Quinto idioma: turquesa
            "#45B7D1",  # Sexto idioma: azul cielo
            "#96CEB4",  # Séptimo idioma: verde menta
            "#FFEAA7",  # Octavo idioma: amarillo claro
        )

        # Si hay más idiomas que colores, usar el último color
        return colores[min(indice, len(colores) - 1)]

    def _escapar_html(self, texto: str) -> str:
        """Escapa caracteres HTML para evitar problemas de renderizado"""
        return texto.replace("<", "&lt;").replace(">", "&gt;")

    def _calcular_caracteres_por_linea(
        self, ancho_label: int, factor_divisor: int = 20, min_caracteres: int = 35
    ) -> int:
        """Calcula cuántos caracteres caben por línea basado en el ancho del label"""
        if ancho_label <= 0:
            ancho_label = 800  # Fallback
        return max(min_caracteres, ancho_label // factor_divisor)

    def _procesar_texto(
        self, texto: str, max_lineas: int = 2, modo: str = "scroll"
    ) -> list:
        """
        Método unificado para procesar texto según el modo especificado

        Args:
            texto: Texto a procesar
            max_lineas: Número máximo de líneas (1 o 2)
            modo: "scroll" para efecto de scroll, "truncate" para truncar

        Returns:
            Lista de líneas procesadas
        """
        try:
            ancho_label = self.label.width() if self.label.width() > 0 else 800

            # Configurar parámetros según el modo y número de líneas
            if max_lineas == 1:
                factor_divisor = 20
                min_caracteres = 40
            else:  # max_lineas == 2
                factor_divisor = 20
                min_caracteres = 35

            caracteres_por_linea = self._calcular_caracteres_por_linea(
                ancho_label, factor_divisor, min_caracteres
            )

            if len(texto) <= caracteres_por_linea:
                return [texto]

            if modo == "scroll":
                return self._aplicar_efecto_scroll(
                    texto, caracteres_por_linea, max_lineas
                )
            else:  # modo == "truncate"
                return self._aplicar_truncado(texto, caracteres_por_linea, max_lineas)

        except Exception as e:
            print(f"Error al procesar texto: {e}")
            # Fallback: dividir por la mitad
            mitad = len(texto) // 2
            return (
                [texto[:mitad], texto[mitad:]]
                if max_lineas > 1
                else [texto[:50] + "..."]
            )

    def _aplicar_efecto_scroll(
        self, texto: str, caracteres_por_linea: int, max_lineas: int
    ) -> list:
        """Aplica efecto de scroll al texto"""
        if max_lineas == 1:
            # Para una línea, mostrar solo la parte final
            if len(texto) > caracteres_por_linea:
                texto_scroll = texto[-(caracteres_por_linea - 3) :]
                return ["..." + texto_scroll]
            return [texto]

        else:  # max_lineas == 2
            # Para dos líneas, dividir el texto
            palabras = texto.split()
            linea1 = ""
            linea2 = ""

            for palabra in palabras:
                if len(linea2) + len(palabra) + 1 <= caracteres_por_linea:
                    if linea2:
                        linea2 += " " + palabra
                    else:
                        linea2 = palabra
                else:
                    linea1 = linea2
                    linea2 = palabra

            lineas = [linea for linea in [linea1, linea2] if linea.strip()]
            return lineas if lineas else [texto[:caracteres_por_linea] + "..."]

    def _aplicar_truncado(
        self, texto: str, caracteres_por_linea: int, max_lineas: int
    ) -> list:
        """Aplica truncado inteligente al texto"""
        if max_lineas == 1:
            # Para una línea, truncar por palabras
            palabras = texto.split()
            texto_truncado = ""
            for palabra in palabras:
                if len(texto_truncado + " " + palabra) <= caracteres_por_linea - 3:
                    if texto_truncado:
                        texto_truncado += " " + palabra
                    else:
                        texto_truncado = palabra
                else:
                    break

            if len(texto_truncado) < len(texto):
                texto_truncado += "..."
            return [texto_truncado]

        else:  # max_lineas == 2
            # Para dos líneas, calcular el máximo total de caracteres
            max_caracteres = caracteres_por_linea * 2

            if len(texto) <= max_caracteres:
                return [texto]

            # Truncar por palabras
            palabras = texto.split()
            texto_resultado = ""
            caracteres_usados = 0

            for palabra in palabras:
                if (
                    caracteres_usados + len(palabra) + 1 > max_caracteres - 3
                ):  # -3 para "..."
                    break
                texto_resultado += palabra + " "
                caracteres_usados += len(palabra) + 1

            if len(texto_resultado.strip()) < len(texto.strip()):
                texto_resultado = texto_resultado.strip() + "..."

            return [texto_resultado.strip()]

    def actualizar_subtitulo(self, texto_nuevo: str, es_final: bool, idioma: str):
        """Actualiza el contenido del globo de texto"""
        # Mostrar el globo si no está visible
        if not self.isVisible():
            self.show()
            self.setWindowOpacity(1.0)
            self._reposicionar()
        elif self.windowOpacity() < 1.0:
            self.setWindowOpacity(1.0)

        # Actualizar el texto para el idioma correspondiente
        self.traducciones_activas[idioma] = texto_nuevo

        # Limpiar traducciones activas si es un solo idioma y es texto final
        if len(self.traducciones_activas) <= 1 and es_final:
            self.traducciones_activas.clear()
            self.traducciones_activas[idioma] = texto_nuevo

        # Generar y aplicar el nuevo contenido HTML con debouncing
        nuevo_html = self._generar_html_subtitulos()
        self.label.setTextDebounced(nuevo_html, delay=30)  # Debouncing muy rápido para subtítulos

        # Ajustar altura automáticamente
        self.adjustSize()

    def _obtener_bandera_idioma(self, idioma):
        """Obtiene la bandera/emoji correspondiente al idioma (optimizado)."""
        # Usar tupla para mejor rendimiento y cachear el split
        codigo = idioma.split("-")[0].lower()
        
        # Diccionario optimizado con get() para mejor rendimiento
        banderas = {
            "es": "🇪🇸", "en": "🇺🇸", "fr": "🇫🇷", "de": "🇩🇪",
            "it": "🇮🇹", "ja": "🇯🇵", "pt": "🇧🇷", "ru": "🇷🇺",
            "zh": "🇨🇳", "ko": "🇰🇷", "ar": "🇸🇦", "hi": "🇮🇳",
        }
        return banderas.get(codigo, "🌐")

    def _reposicionar(self):
        """Posiciona la ventana en la parte inferior central de la pantalla"""
        if not self.posicion_inicial_establecida:
            screen = self.screen()
            if not screen:
                return
            screen_geometry = screen.availableGeometry()
            x = screen_geometry.center().x() - self.width() // 2
            y = screen_geometry.height() - self.height() - 60
            self.move(x, y)
            self.posicion_inicial_establecida = True

    def showEvent(self, event):
        """Se activa cuando la ventana se muestra"""
        super().showEvent(event)
        self._calcular_y_establecer_ancho()
        self.adjustSize()
        self._reposicionar()
        self.setWindowOpacity(1.0)

    def mousePressEvent(self, event):
        """Inicia el arrastre cuando se presiona el botón izquierdo del mouse"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = (
                event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            )
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Arrastra la ventana cuando se mueve el mouse mientras se mantiene presionado"""
        if (
            self.drag_position is not None
            and event.buttons() == Qt.MouseButton.LeftButton
        ):
            nueva_posicion = event.globalPosition().toPoint() - self.drag_position
            screen = self.screen()
            if screen:
                screen_geometry = screen.availableGeometry()
                x = max(
                    0, min(nueva_posicion.x(), screen_geometry.width() - self.width())
                )
                y = max(
                    0, min(nueva_posicion.y(), screen_geometry.height() - self.height())
                )
                self.move(x, y)
            else:
                self.move(nueva_posicion)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """Termina el arrastre cuando se suelta el botón del mouse"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = None
            self.setCursor(Qt.CursorShape.ArrowCursor)
        super().mouseReleaseEvent(event)

    def enterEvent(self, event):
        """Cambia el cursor cuando el mouse entra en la ventana"""
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Restaura el cursor cuando el mouse sale de la ventana"""
        if self.drag_position is None:
            self.setCursor(Qt.CursorShape.ArrowCursor)
        super().leaveEvent(event)


class ModernComboBox(QComboBox):
    """ComboBox con estilo moderno"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(StyleManager.get_modern_combo_style())


class ConfigDialog(QDialog):
    """Diálogo para configurar las credenciales de Azure"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("⚙️ Configuración de Azure")
        self.setFixedSize(500, 350)
        self.setWindowFlags(
            Qt.WindowType.Dialog
            | Qt.WindowType.WindowTitleHint
            | Qt.WindowType.WindowCloseButtonHint
        )
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Título
        title = QLabel("🔧 Configuración de Azure Speech Service")
        title.setStyleSheet(StyleManager.get_title_style())
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # API Key
        key_layout = QVBoxLayout()
        key_label = QLabel("🔑 Azure Speech Key:")
        key_label.setStyleSheet(StyleManager.get_label_style())
        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("Ingresa tu Azure Speech Key...")
        self.key_input.setText(AZURE_SPEECH_KEY)
        self.key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.key_input.setStyleSheet(StyleManager.get_input_style())
        key_layout.addWidget(key_label)
        key_layout.addWidget(self.key_input)
        layout.addLayout(key_layout)

        # Región
        region_layout = QVBoxLayout()
        region_label = QLabel("🌍 Azure Region:")
        region_label.setStyleSheet(StyleManager.get_label_style())
        self.region_input = QLineEdit()
        self.region_input.setPlaceholderText("ej: eastus, westus2, westeurope...")
        self.region_input.setText(AZURE_SPEECH_REGION)
        self.region_input.setStyleSheet(StyleManager.get_input_style())
        region_layout.addWidget(region_label)
        region_layout.addWidget(self.region_input)
        layout.addLayout(region_layout)

        # Botones
        button_layout = QHBoxLayout()

        self.reset_button = QPushButton("🔄 Restaurar")
        self.reset_button.setStyleSheet(
            StyleManager.get_button_style("#6C757D", "#5A6268", "#7A8288", "#6C757D")
        )
        self.reset_button.clicked.connect(self.reset_to_default)

        self.cancel_button = QPushButton("❌ Cancelar")
        self.cancel_button.setStyleSheet(
            StyleManager.get_button_style("#DC3545", "#C82333", "#E74C3C", "#DC3545")
        )
        self.cancel_button.clicked.connect(self.reject)

        self.save_button = QPushButton("✅ Guardar")
        self.save_button.setStyleSheet(
            StyleManager.get_button_style("#28A745", "#1E7E34", "#34CE57", "#28A745")
        )
        self.save_button.clicked.connect(self.save_config)

        button_layout.addWidget(self.reset_button)
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.save_button)
        layout.addLayout(button_layout)

        # Estilo del diálogo
        self.setStyleSheet(StyleManager.get_dialog_style())

    def reset_to_default(self):
        """Restaura los valores por defecto"""
        from traductor_azure.src.config import DEFAULT_AZURE_SPEECH_KEY, DEFAULT_AZURE_SPEECH_REGION

        self.key_input.setText(DEFAULT_AZURE_SPEECH_KEY)
        self.region_input.setText(DEFAULT_AZURE_SPEECH_REGION)

    def save_config(self):
        """Guarda la configuración"""
        key = self.key_input.text().strip()
        region = self.region_input.text().strip()

        if not key or not region:
            QMessageBox.warning(self, "Error", "Por favor, completa ambos campos.")
            return

        if key == "PegaTuClaveAqui" or region == "PegaTuRegionAqui":
            QMessageBox.warning(
                self, "Error", "Por favor, ingresa credenciales válidas de Azure."
            )
            return

        # Actualizar las credenciales (ahora guarda automáticamente en archivo)
        success = update_azure_credentials(key, region)

        if success:
            QMessageBox.information(
                self,
                "Éxito",
                "✅ Configuración guardada correctamente.\n\nLos cambios se han guardado permanentemente y se aplicarán en la próxima sesión.",
            )
        else:
            QMessageBox.warning(
                self,
                "Error",
                "❌ Error al guardar la configuración.\n\nLos cambios se aplicarán solo para esta sesión.",
            )

        self.accept()


class VentanaSubtitulos(QWidget):
    def __init__(self):
        super().__init__()
        self.worker = None
        self.is_translating = False
        self.ventana_flotante = VentanaFlotante()
        self.session_data = []  # Lista para almacenar todo lo hablado durante la sesión
        self.save_worker = None  # Worker para guardado asíncrono
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("🎤 NexoVoz - Traductor de Subtítulos en Vivo")
        self.setGeometry(200, 200, 900, 600)

        # Estilo general más moderno
        self.setStyleSheet(StyleManager.get_main_window_style())

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(25, 25, 25, 25)

        # Título principal con estilo
        title_layout = QHBoxLayout()

        title_label = QLabel("🎤 NexoVoz")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(StyleManager.get_title_label_style())

        # Botón de configuración de Azure
        self.config_button = QPushButton("⚙️")
        self.config_button.setFixedSize(40, 40)
        self.config_button.setToolTip("Configurar credenciales de Azure")
        self.config_button.setStyleSheet(StyleManager.get_config_button_style())
        self.config_button.clicked.connect(self.open_config)

        # Botón de configuración de audio
        self.audio_config_button = QPushButton("🎤")
        self.audio_config_button.setFixedSize(40, 40)
        self.audio_config_button.setToolTip(
            "Configurar audio para captura omnidireccional"
        )
        self.audio_config_button.setStyleSheet(StyleManager.get_config_button_style())
        self.audio_config_button.clicked.connect(self.open_audio_config)

        # Botón de información sobre cuota de Azure
        self.quota_info_button = QPushButton("ℹ️")
        self.quota_info_button.setFixedSize(40, 40)
        self.quota_info_button.setToolTip("Información sobre cuota de Azure Speech Services")
        self.quota_info_button.setStyleSheet(StyleManager.get_config_button_style())
        self.quota_info_button.clicked.connect(self.show_quota_info)

        # Agregar título y botones al layout horizontal
        title_layout.addWidget(title_label)
        title_layout.addStretch()  # Empuja todo a la izquierda
        title_layout.addWidget(self.quota_info_button)
        title_layout.addWidget(self.audio_config_button)
        title_layout.addWidget(self.config_button)

        # Agregar el layout del título al layout principal
        main_layout.addLayout(title_layout)

        # El resto del código continúa igual...

        # Tarjeta de controles
        controls_card = ModernCard()
        controls_layout = QVBoxLayout(controls_card)
        controls_layout.setContentsMargins(15, 15, 15, 15)

        # Título de la sección
        controls_title = QLabel("⚙️ Configuración")
        controls_title.setStyleSheet(StyleManager.get_controls_title_style())
        controls_layout.addWidget(controls_title)

        # Layout de idiomas
        languages_layout = QVBoxLayout()

        # Idioma de entrada
        source_layout = QVBoxLayout()
        source_label = QLabel("🎤 Idioma de Entrada:")
        source_label.setStyleSheet(StyleManager.get_section_label_style())
        self.combo_source = ModernComboBox()
        self.combo_source.addItems(LANGUAGES.keys())
        source_layout.addWidget(source_label)
        source_layout.addWidget(self.combo_source)

        # Idiomas de salida múltiples
        target_layout = QVBoxLayout()
        target_label = QLabel("🌐 Idiomas de Salida (máximo 3):")
        target_label.setStyleSheet(StyleManager.get_section_label_style())

        # Crear scroll area para los checkboxes de idiomas
        scroll_area = QScrollArea()
        scroll_area.setMaximumHeight(120)
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet(StyleManager.get_scroll_area_style())

        # Widget contenedor para los checkboxes
        self.checkboxes_container = QWidget()
        self.checkboxes_layout = QVBoxLayout(self.checkboxes_container)
        self.checkboxes_layout.setContentsMargins(10, 5, 10, 5)

        # Crear checkboxes para cada idioma
        self.idioma_checkboxes = {}
        for idioma in TRANSLATE_CODES.keys():
            checkbox = QCheckBox(idioma)
            checkbox.setStyleSheet(StyleManager.get_checkbox_style())
            checkbox.stateChanged.connect(self.on_idioma_selection_changed)
            self.idioma_checkboxes[idioma] = checkbox
            self.checkboxes_layout.addWidget(checkbox)

        scroll_area.setWidget(self.checkboxes_container)

        target_layout.addWidget(target_label)
        target_layout.addWidget(scroll_area)

        # Layout horizontal para entrada y salida
        languages_horizontal = QHBoxLayout()
        languages_horizontal.addLayout(source_layout)
        languages_horizontal.addStretch()
        languages_horizontal.addLayout(target_layout)

        languages_layout.addLayout(languages_horizontal)

        controls_layout.addLayout(languages_layout)

        # Botón principal con estilo moderno
        self.toggle_button = QPushButton("🚀 Iniciar Traducción")
        self.toggle_button.setStyleSheet(StyleManager.get_toggle_button_start_style())
        self.toggle_button.clicked.connect(self.toggle_translation)
        controls_layout.addWidget(self.toggle_button)

        # Botón para guardar sesión en MongoDB y localmente
        self.save_button = QPushButton("💾 Guardar Sesión")
        self.save_button.setStyleSheet(StyleManager.get_save_button_style())
        self.save_button.clicked.connect(self.guardar_sesion)
        self.save_button.setEnabled(False)  # Deshabilitado inicialmente
        controls_layout.addWidget(self.save_button)

        main_layout.addWidget(controls_card)

        # Tarjetas de contenido
        content_layout = QHBoxLayout()

        # Tarjeta de texto original
        original_card = ModernCard()
        original_layout = QVBoxLayout(original_card)
        original_layout.setContentsMargins(20, 20, 20, 20)

        original_title = QLabel("🗣️ Transcripción Original")
        original_title.setStyleSheet(StyleManager.get_card_title_style())

        self.label_original = DebouncedLabel("[Esperando audio...]", delay=100)
        self.label_original.setWordWrap(True)
        self.label_original.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft
        )
        self.label_original.setMinimumHeight(150)

        original_layout.addWidget(original_title)
        original_layout.addWidget(self.label_original)

        # Tarjeta de traducción
        translated_card = ModernCard()
        translated_layout = QVBoxLayout(translated_card)
        translated_layout.setContentsMargins(20, 20, 20, 20)

        translated_title = QLabel("💬 Traducción")
        translated_title.setStyleSheet(StyleManager.get_card_title_style())

        self.label_translated = DebouncedLabel("[La traducción aparecerá aquí...]", delay=100)
        self.label_translated.setWordWrap(True)
        self.label_translated.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft
        )
        self.label_translated.setMinimumHeight(150)

        translated_layout.addWidget(translated_title)
        translated_layout.addWidget(self.label_translated)

        content_layout.addWidget(original_card)
        content_layout.addWidget(translated_card)

        main_layout.addLayout(content_layout)

        # Barra de estado moderna
        status_card = ModernCard()
        status_layout = QVBoxLayout(status_card)
        status_layout.setContentsMargins(20, 15, 20, 15)

        self.label_estado = QLabel("✅ Listo para iniciar")
        self.label_estado.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_estado.setStyleSheet(StyleManager.get_status_ready_style())

        status_layout.addWidget(self.label_estado)
        main_layout.addWidget(status_card)

        # Inicializar con un idioma por defecto seleccionado
        if "Inglés (EE.UU.)" in self.idioma_checkboxes:
            self.idioma_checkboxes["Inglés (EE.UU.)"].setChecked(True)

    def on_idioma_selection_changed(self):
        """Maneja los cambios en la selección de idiomas de salida"""
        idiomas_seleccionados = []
        for idioma, checkbox in self.idioma_checkboxes.items():
            if checkbox.isChecked():
                idiomas_seleccionados.append(idioma)

        # Limitar a máximo 3 idiomas
        if len(idiomas_seleccionados) > 3:
            # Desmarcar el último seleccionado
            for idioma, checkbox in reversed(list(self.idioma_checkboxes.items())):
                if checkbox.isChecked() and idioma not in idiomas_seleccionados[:3]:
                    checkbox.setChecked(False)
                    break

        # Actualizar el estado del botón
        idiomas_actuales = [
            idioma
            for idioma, checkbox in self.idioma_checkboxes.items()
            if checkbox.isChecked()
        ]
        if idiomas_actuales:
            self.toggle_button.setEnabled(True)
            self.toggle_button.setText(
                f"🚀 Iniciar Traducción ({len(idiomas_actuales)} idiomas)"
            )
        else:
            self.toggle_button.setEnabled(False)
            self.toggle_button.setText("🚀 Selecciona al menos un idioma")

    def get_idiomas_seleccionados(self):
        """Retorna la lista de idiomas seleccionados"""
        return [
            idioma
            for idioma, checkbox in self.idioma_checkboxes.items()
            if checkbox.isChecked()
        ]

    def toggle_translation(self):
        if self.is_translating:
            # Detener traducción de forma segura
            if self.worker and self.worker.isRunning():
                self.worker.stop()
                if not self.worker.wait(2000):  # Esperar máximo 2 segundos
                    self.worker.terminate()
                    self.worker.wait(1000)
                self.worker.deleteLater()
                self.worker = None
            
            self.is_translating = False
            self.toggle_button.setText("🚀 Iniciar Traducción")
            self.toggle_button.setStyleSheet(StyleManager.get_toggle_button_start_style())
            self.label_estado.setText("⏹️ Detenido. Listo para iniciar.")
            self.label_estado.setStyleSheet(StyleManager.get_status_ready_style())
            self.ventana_flotante.hide()
            # Habilitar botón de guardar si hay datos
            self.save_button.setEnabled(len(self.session_data) > 0)
        else:
            # Verificar credenciales antes de iniciar
            from traductor_azure.src.config import AZURE_SPEECH_KEY, AZURE_SPEECH_REGION

            if (
                AZURE_SPEECH_KEY == "PegaTuClaveAqui"
                or AZURE_SPEECH_REGION == "PegaTuRegionAqui"
            ):
                self.label_estado.setText(
                    "❌ Configura las credenciales de Azure primero"
                )
                self.label_estado.setStyleSheet(StyleManager.get_status_error_style())
                return

            # Verificar que hay idiomas seleccionados
            idiomas_seleccionados = self.get_idiomas_seleccionados()
            if not idiomas_seleccionados:
                self.label_estado.setText("❌ Selecciona al menos un idioma de salida")
                self.label_estado.setStyleSheet(StyleManager.get_status_error_style())
                return

            # Limpiar sesión anterior al iniciar nueva traducción
            self.session_data = []
            self.ventana_flotante.traducciones_activas = {}
            self.ventana_flotante.label.setText("Iniciando...")

            source_lang = LANGUAGES[self.combo_source.currentText()]
            target_langs = [TRANSLATE_CODES[idioma] for idioma in idiomas_seleccionados]

            self.worker = WorkerStreaming(source_lang, target_langs)
            self.worker.subtitulos_actualizados.connect(self.actualizar_texto)
            self.worker.estado_actualizado.connect(self.actualizar_estado)
            self.worker.finished.connect(self.translation_finished)
            self.worker.start()

            self.is_translating = True
            self.toggle_button.setText("⏹️ Detener Traducción")
            self.toggle_button.setStyleSheet(StyleManager.get_toggle_button_stop_style())

            self.label_estado.setText("🔄 Iniciando worker...")
            self.label_estado.setStyleSheet(StyleManager.get_status_working_style())
            self.ventana_flotante.show()
            # Deshabilitar botón de guardar al iniciar nueva sesión
            self.save_button.setEnabled(False)

    def actualizar_texto(self, texto_original, traducciones, es_final):
        # Usar debouncing para actualizaciones de UI
        self.label_original.setTextDebounced(f"🗣️ {texto_original}", delay=50)

        # Manejar múltiples traducciones
        if isinstance(traducciones, dict):
            # Múltiples idiomas - optimizar con join
            texto_traducciones = []
            for idioma, texto in traducciones.items():
                if texto.strip():
                    bandera = self.ventana_flotante._obtener_bandera_idioma(idioma)
                    texto_traducciones.append(f"{bandera} {texto.strip()}")

            texto_final = (
                "\n".join(texto_traducciones)
                if texto_traducciones
                else "Traduciendo..."
            )
            self.label_translated.setTextDebounced(f"💬 {texto_final}", delay=50)

            # Actualizar ventana flotante con múltiples idiomas
            if self.is_translating:
                for idioma, texto in traducciones.items():
                    self.ventana_flotante.actualizar_subtitulo(texto, es_final, idioma)
        else:
            # Modo legacy - un solo idioma
            self.label_translated.setTextDebounced(f"💬 {traducciones}", delay=50)
            if self.is_translating:
                # En modo legacy, traducciones es un string, no un diccionario
                # Usar el primer idioma seleccionado como idioma por defecto
                idiomas_seleccionados = self.get_idiomas_seleccionados()
                if idiomas_seleccionados:
                    idioma_por_defecto = TRANSLATE_CODES[idiomas_seleccionados[0]]
                    self.ventana_flotante.actualizar_subtitulo(
                        traducciones, es_final, idioma_por_defecto
                    )

        # Guardar en la sesión solo si es texto final (completo)
        if es_final and texto_original.strip():
            from datetime import datetime

            timestamp = datetime.now().strftime("%H:%M:%S")

            if isinstance(traducciones, dict):
                # Múltiples idiomas
                traducciones_guardar = {
                    idioma: texto
                    for idioma, texto in traducciones.items()
                    if texto.strip()
                }
                if traducciones_guardar:
                    self.session_data.append(
                        {
                            "timestamp": timestamp,
                            "original": texto_original.strip(),
                            "translations": traducciones_guardar,
                        }
                    )
            else:
                # Un solo idioma
                if traducciones.strip():
                    self.session_data.append(
                        {
                            "timestamp": timestamp,
                            "original": texto_original.strip(),
                            "translated": traducciones.strip(),
                        }
                    )

            # Habilitar botón de guardar cuando se agregue contenido
            self.save_button.setEnabled(True)

    def actualizar_estado(self, estado):
        self.label_estado.setText(f"🔄 {estado}")

    def translation_finished(self):
        self.is_translating = False
        if "ERROR" not in self.label_estado.text():
            self.label_estado.setText("✅ Detenido.")
            self.label_estado.setStyleSheet(StyleManager.get_status_ready_style())

        self.toggle_button.setText("🚀 Iniciar Traducción")
        self.toggle_button.setStyleSheet(StyleManager.get_toggle_button_start_style())
        self.ventana_flotante.hide()

    def open_config(self):
        """Abre el diálogo de configuración de Azure"""
        dialog = ConfigDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Si se guardó la configuración, reiniciar el worker si está activo
            if self.is_translating:
                # Detener el worker actual
                if self.worker:
                    self.worker.stop()
                    self.worker.wait()

                # Reiniciar con las nuevas credenciales
                idiomas_seleccionados = self.get_idiomas_seleccionados()
                source_lang = LANGUAGES[self.combo_source.currentText()]
                target_langs = [TRANSLATE_CODES[idioma] for idioma in idiomas_seleccionados]
                
                self.worker = WorkerStreaming(source_lang, target_langs)
                self.worker.subtitulos_actualizados.connect(self.actualizar_texto)
                self.worker.estado_actualizado.connect(self.actualizar_estado)
                self.worker.start()

    def open_audio_config(self):
        """Abre el diálogo de configuración de audio para captura omnidireccional"""
        dialog = AudioConfigDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Si se guardó la configuración de audio, reiniciar el worker si está activo
            if self.is_translating:
                # Detener el worker actual
                if self.worker:
                    self.worker.stop()
                    self.worker.wait()

                # Reiniciar con las nuevas configuraciones de audio
                idiomas_seleccionados = self.get_idiomas_seleccionados()
                source_lang = LANGUAGES[self.combo_source.currentText()]
                target_langs = [TRANSLATE_CODES[idioma] for idioma in idiomas_seleccionados]
                
                self.worker = WorkerStreaming(source_lang, target_langs)
                self.worker.subtitulos_actualizados.connect(self.actualizar_texto)
                self.worker.estado_actualizado.connect(self.actualizar_estado)
                self.worker.start()

                # Mostrar mensaje de confirmación
                QMessageBox.information(
                    self,
                    "Configuración de Audio",
                    "✅ Configuración de audio actualizada.\n"
                    "Las nuevas configuraciones se aplicarán en la próxima sesión de traducción.",
                )

    def guardar_sesion(self):
        """Guarda la sesión actual solo en MongoDB Atlas (asíncrono)"""
        try:
            if not self.session_data:
                self.label_estado.setText("⚠️ No hay datos para guardar")
                return None

            # Verificar si ya hay un guardado en progreso
            if self.save_worker and self.save_worker.isRunning():
                self.label_estado.setText("⏳ Guardando... Por favor espera")
                return None

            from datetime import datetime

            # Obtener idiomas de la sesión actual
            source_lang = LANGUAGES[self.combo_source.currentText()]
            target_langs = [
                TRANSLATE_CODES[idioma] for idioma in self.get_idiomas_seleccionados()
            ]

            # Crear timestamp para el nombre de la sesión
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            session_name = f"nexovoz_sesion_{timestamp}"

            # Crear y configurar el worker asíncrono
            self.save_worker = SaveWorker(
                self.session_data, source_lang, target_langs, session_name
            )
            self.save_worker.save_completed.connect(self.on_save_completed)

            # Mostrar estado de guardado
            self.label_estado.setText("⏳ Guardando en MongoDB y localmente...")
            self.save_button.setEnabled(False)
            self.save_button.setText("⏳ Guardando...")

            # Iniciar el guardado asíncrono
            self.save_worker.start()

            print(f"🔄 Iniciando guardado asíncrono: {session_name}")
            return session_name

        except Exception as e:
            error_msg = f"❌ Error al iniciar guardado: {str(e)[:50]}..."
            self.label_estado.setText(error_msg)
            print(f"❌ Error en guardar_sesion: {e}")

            # Restaurar estado del botón en caso de error
            self.save_button.setEnabled(True)
            self.save_button.setText("💾 Guardar Sesión")

            return None

    def on_save_completed(self, success, message):
        """Maneja la finalización del guardado asíncrono"""
        try:
            self.label_estado.setText(message)
            self.save_button.setText("💾 Guardar Sesión")

            if success:
                print("✅ Guardado en MongoDB y localmente completado exitosamente")
                self.save_button.setEnabled(
                    False
                )  # Deshabilitar después de guardar exitosamente
            else:
                print("❌ Error en el guardado")
                self.save_button.setEnabled(True)  # Rehabilitar si hubo error
                print(f"❌ Detalles del error: {message}")

            # Limpiar el workerF
            if self.save_worker:
                self.save_worker.deleteLater()
                self.save_worker = None

        except Exception as e:
            print(f"❌ Error en on_save_completed: {e}")
            # Restaurar estado en caso de error
            self.save_button.setEnabled(True)
            self.save_button.setText("💾 Guardar Sesión")
            self.label_estado.setText("❌ Error al procesar resultado del guardado")

    def closeEvent(self, event):
        """Maneja el cierre de la ventana con limpieza optimizada de recursos"""
        try:
            # Detener el worker de traducción de forma segura
            if self.worker and self.worker.isRunning():
                self.worker.stop()
                if not self.worker.wait(3000):  # Esperar máximo 3 segundos
                    self.worker.terminate()
                    self.worker.wait(1000)  # Esperar 1 segundo más
                self.worker.deleteLater()
                self.worker = None

            # Cerrar ventana flotante
            if self.ventana_flotante:
                self.ventana_flotante.close()
                self.ventana_flotante = None

            # Limpiar worker de guardado si está activo
            if self.save_worker and self.save_worker.isRunning():
                self.save_worker.terminate()
                if not self.save_worker.wait(2000):  # Esperar máximo 2 segundos
                    self.save_worker.terminate()
                self.save_worker.deleteLater()
                self.save_worker = None

        except Exception as e:
            print(f"⚠️ Error durante limpieza: {e}")
        finally:
            event.accept()

    def show_quota_info(self):
        """Muestra información sobre la cuota de Azure Speech Services"""
        from PyQt6.QtWidgets import QMessageBox
        
        info_text = """
        <h3>📊 Información sobre Cuota de Azure Speech Services</h3>
        
        <p><b>Plan Gratuito:</b></p>
        <ul>
        <li>5 horas de audio por mes</li>
        <li>Se renueva mensualmente</li>
        <li>Límite de 20,000 transacciones por mes</li>
        </ul>
        
        <p><b>Si has excedido la cuota:</b></p>
        <ul>
        <li>⏰ Espera hasta el próximo ciclo de facturación</li>
        <li>🆕 Crea una nueva cuenta de Azure gratuita</li>
        <li>💳 Actualiza a plan de pago en portal.azure.com</li>
        </ul>
        
        <p><b>Verificar cuota:</b></p>
        <ul>
        <li>Ve a portal.azure.com</li>
        <li>Selecciona tu recurso de Speech Services</li>
        <li>Revisa la sección "Métricas"</li>
        </ul>
        
        <p><b>Error Code 1007:</b> Cuota excedida</p>
        <p><b>Error Code 401:</b> Credenciales inválidas</p>
        """
        
        msg = QMessageBox(self)
        msg.setWindowTitle("ℹ️ Información sobre Cuota de Azure")
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setText(info_text)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.exec()
