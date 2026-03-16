"""
Gestor centralizado de estilos CSS para Amazon Translator
Diseño inspirado en la Amazonía con colores frescos y naturales
"""


class StyleManager:
    """Gestor centralizado de estilos CSS para la aplicación"""

    # Paleta de colores Amazonía
    AMAZON_GREEN = "#00D084"  # Verde amazonas vibrante
    AMAZON_DARK = "#008F5D"   # Verde oscuro
    SKY_BLUE = "#4FC3F7"      # Azul cielo
    LIGHT_BLUE = "#81D4FA"    # Azul claro
    FOREST_GREEN = "#26A69A"  # Verde bosque
    WHITE = "#FFFFFF"
    LIGHT_GRAY = "#F5F5F5"
    MEDIUM_GRAY = "#E0E0E0"
    TEXT_DARK = "#2C3E50"
    TEXT_LIGHT = "#607D8B"

    @staticmethod
    def get_modern_combo_style():
        """Estilo para ModernComboBox"""
        return """
            QComboBox {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #FFFFFF,
                                          stop: 1 #F5F9FC);
                border: 2px solid #81D4FA;
                border-radius: 20px;
                padding: 8px 15px;
                font-size: 14px;
                font-weight: 500;
                color: #2C3E50;
                min-width: 160px;
                max-height: 40px;
            }
            
            QComboBox:hover {
                border-color: #4FC3F7;
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #F0F8FF,
                                          stop: 1 #E1F5FE);
                box-shadow: 0 2px 8px rgba(79, 195, 247, 0.3);
            }
            
            QComboBox:focus {
                border-color: #00D084;
                outline: none;
            }
            
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 30px;
                border-left: 2px solid #E0E0E0;
                border-top-right-radius: 18px;
                border-bottom-right-radius: 18px;
                background: transparent;
            }
            
            QComboBox::down-arrow {
                image: none;
                border-left: 6px solid transparent;
                border-right: 6px solid transparent;
                border-top: 6px solid #4FC3F7;
                width: 0;
                height: 0;
            }
            
            QComboBox QAbstractItemView {
                background-color: #FFFFFF;
                border: 2px solid #4FC3F7;
                border-radius: 15px;
                selection-background-color: #00D084;
                selection-color: #FFFFFF;
                color: #2C3E50;
                padding: 5px;
            }
        """

    @staticmethod
    def get_title_style():
        """Estilo para títulos principales"""
        return """
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: #00D084;
                background: transparent;
                border: none;
                padding: 12px 0;
                margin-bottom: 10px;
            }
        """

    @staticmethod
    def get_label_style():
        """Estilo para etiquetas"""
        return """
            QLabel {
                font-size: 14px;
                font-weight: 600;
                color: #2C3E50;
                background: transparent;
                border: none;
                padding: 6px 0;
            }
        """

    @staticmethod
    def get_input_style():
        """Estilo para campos de entrada"""
        return """
            QLineEdit {
                background-color: #FFFFFF;
                border: 2px solid #E0E0E0;
                border-radius: 20px;
                padding: 12px 18px;
                font-size: 14px;
                color: #2C3E50;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLineEdit:focus {
                border-color: #4FC3F7;
                background-color: #F0F8FF;
                box-shadow: 0 2px 8px rgba(79, 195, 247, 0.2);
            }
            QLineEdit:hover {
                border-color: #81D4FA;
            }
        """

    @staticmethod
    def get_button_style(color_start, color_end, hover_start=None, hover_end=None):
        """Estilo para botones con colores personalizables"""
        hover_start = hover_start or color_start
        hover_end = hover_end or color_end
        return f"""
            QPushButton {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 {color_start},
                                            stop: 1 {color_end});
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 25px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 {hover_start},
                                            stop: 1 {hover_end});
                box-shadow: 0 4px 12px rgba(0, 208, 132, 0.3);
                transform: translateY(-2px);
            }}
            QPushButton:pressed {{
                transform: translateY(0px);
            }}
        """

    @staticmethod
    def get_dialog_style():
        """Estilo para diálogos"""
        return """
            QDialog {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 #FFFFFF,
                                            stop: 1 #F0F8FF);
                color: #2C3E50;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """

    @staticmethod
    def get_main_window_style():
        """Estilo para la ventana principal - Tema Amazon"""
        return """
            QWidget {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 #E8F5E9,
                                            stop: 0.5 #F0F8FF,
                                            stop: 1 #E1F5FE);
                color: #2C3E50;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            
            QLabel {
                color: #2C3E50;
                background: transparent;
                border: none;
            }
            
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 #FFFFFF,
                                            stop: 1 #F5F5F5);
                border: 2px solid #E0E0E0;
                border-radius: 20px;
                padding: 10px 20px;
                font-weight: 600;
                color: #2C3E50;
            }
            
            QPushButton:hover {
                border-color: #4FC3F7;
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 #F0F8FF,
                                            stop: 1 #E1F5FE);
                box-shadow: 0 4px 12px rgba(79, 195, 247, 0.3);
            }
            
            QPushButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 #E1F5FE,
                                            stop: 1 #F0F8FF);
            }
            
            QPushButton:disabled {
                background: #F5F5F5;
                color: #BDBDBD;
                border-color: #E0E0E0;
            }
        """

    @staticmethod
    def get_title_label_style():
        """Estilo para el título principal Amazon Translator"""
        return """
            QLabel {
                font-size: 32px;
                font-weight: bold;
                color: #00D084;
                background: transparent;
                border: none;
                padding: 15px 0;
                margin-bottom: 10px;
            }
        """

    @staticmethod
    def get_config_button_style():
        """Estilo para botones de configuración"""
        return """
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 #FFFFFF,
                                            stop: 1 #F5F9FC);
                border: 2px solid #81D4FA;
                border-radius: 25px;
                color: #2C3E50;
                font-size: 16px;
                font-weight: bold;
                min-width: 50px;
                min-height: 50px;
            }
            QPushButton:hover {
                border-color: #4FC3F7;
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 #E1F5FE,
                                            stop: 1 #B3E5FC);
                box-shadow: 0 4px 15px rgba(79, 195, 247, 0.4);
                transform: scale(1.05);
            }
        """

    @staticmethod
    def get_controls_title_style():
        """Estilo para títulos de secciones"""
        return """
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #4FC3F7;
                background: transparent;
                border: none;
                padding: 8px 0;
                margin-bottom: 8px;
            }
        """

    @staticmethod
    def get_section_label_style():
        """Estilo para etiquetas de secciones"""
        return """
            QLabel {
                font-size: 14px;
                font-weight: 600;
                color: #2C3E50;
                background: transparent;
                border: none;
                padding: 5px 0;
            }
        """

    @staticmethod
    def get_scroll_area_style():
        """Estilo para áreas de scroll"""
        return """
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollArea > QWidget > QWidget {
                background: transparent;
            }
            QScrollBar:vertical {
                background: #F5F5F5;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #81D4FA;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #4FC3F7;
            }
        """

    @staticmethod
    def get_checkbox_style():
        """Estilo para checkboxes - Tema Amazon"""
        return """
            QCheckBox {
                color: #2C3E50;
                background: transparent;
                border: none;
                padding: 4px;
                spacing: 10px;
                font-weight: 500;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border: 2px solid #81D4FA;
                border-radius: 6px;
                background: #FFFFFF;
            }
            QCheckBox::indicator:checked {
                background: #00D084;
                border-color: #00D084;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iMTIiIHZpZXdCb3g9IjAgMCAxMiAxMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEwIDNMNC41IDguNUwyIDYiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+Cjwvc3ZnPgo=);
            }
            QCheckBox::indicator:hover {
                border-color: #4FC3F7;
                background: #F0F8FF;
            }
            QCheckBox::indicator:checked:hover {
                background: #26A69A;
                border-color: #26A69A;
            }
        """

    @staticmethod
    def get_toggle_button_start_style():
        """Estilo para botón de inicio - Verde Amazonía"""
        return """
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 #00D084,
                                            stop: 1 #26A69A);
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 30px;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 #26E099,
                                            stop: 1 #00D084);
                box-shadow: 0 6px 20px rgba(0, 208, 132, 0.4);
            }
            QPushButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 #008F5D,
                                            stop: 1 #00D084);
                transform: scale(0.98);
            }
        """

    @staticmethod
    def get_toggle_button_stop_style():
        """Estilo para botón de detener - Naranja Atardecer"""
        return """
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 #FF9800,
                                            stop: 1 #F57C00);
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 30px;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 #FFB74D,
                                            stop: 1 #FF9800);
                box-shadow: 0 6px 20px rgba(255, 152, 0, 0.4);
            }
            QPushButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 #F57C00,
                                            stop: 1 #FF9800);
                transform: scale(0.98);
            }
        """

    @staticmethod
    def get_save_button_style():
        """Estilo para botón de guardar - Azul cielo"""
        return """
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 #4FC3F7,
                                            stop: 1 #0288D1);
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 25px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 #81D4FA,
                                            stop: 1 #4FC3F7);
                box-shadow: 0 4px 15px rgba(79, 195, 247, 0.5);
            }
            QPushButton:disabled {
                background: #E0E0E0;
                color: #9E9E9E;
            }
        """

    @staticmethod
    def get_card_title_style():
        """Estilo para títulos de tarjetas"""
        return """
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #26A69A;
                background: transparent;
                border: none;
                padding: 8px 0;
                margin-bottom: 10px;
            }
        """

    @staticmethod
    def get_status_ready_style():
        """Estilo para estado listo"""
        return """
            QLabel {
                font-size: 14px;
                font-weight: 600;
                color: #00D084;
                background: transparent;
                border: none;
                padding: 6px;
            }
        """

    @staticmethod
    def get_status_error_style():
        """Estilo para estado de error"""
        return """
            QLabel {
                font-size: 14px;
                font-weight: 600;
                color: #F44336;
                background: transparent;
                border: none;
                padding: 6px;
            }
        """

    @staticmethod
    def get_status_working_style():
        """Estilo para estado trabajando"""
        return """
            QLabel {
                font-size: 14px;
                font-weight: 600;
                color: #FF9800;
                background: transparent;
                border: none;
                padding: 6px;
            }
        """

    @staticmethod
    def get_globe_style():
        """Estilo para el globo de texto - Tema claro"""
        return """
            QLabel {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 rgba(255, 255, 255, 250),
                                          stop: 1 rgba(240, 248, 255, 250));
                color: #2C3E50;
                padding: 30px 40px;
                border-radius: 25px;
                border: 2px solid rgba(79, 195, 247, 120);
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 15px;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
            }
        """

    @staticmethod
    def get_modern_card_style():
        """Estilo para tarjetas modernas - Tema Amazon"""
        return """
            ModernCard {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #FFFFFF,
                                          stop: 1 #F9FFFE);
                border-radius: 20px;
                border: 2px solid #E0F2F1;
                box-shadow: 0 4px 15px rgba(0, 208, 132, 0.1);
            }
        """

    @staticmethod
    def get_text_area_style():
        """Estilo para áreas de texto grandes"""
        return """
            QTextEdit, QPlainTextEdit {
                background-color: #FFFFFF;
                border: 2px solid #E0E0E0;
                border-radius: 15px;
                padding: 15px;
                font-size: 14px;
                color: #2C3E50;
                font-family: 'Segoe UI', Arial, sans-serif;
                line-height: 1.6;
            }
            QTextEdit:focus, QPlainTextEdit:focus {
                border-color: #4FC3F7;
                background-color: #FAFFFE;
            }
        """