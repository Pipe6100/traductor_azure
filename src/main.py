# main.py

import sys
import time
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from traductor_azure.src.config import AZURE_SPEECH_KEY, AZURE_SPEECH_REGION
from traductor_azure.src.ui import VentanaSubtitulos


class Application:
    """
    Clase principal que gestiona el flujo de la aplicación:
    Muestra directamente la ventana principal de subtítulos.
    """

    def __init__(self):
        # Verificación de credenciales antes de iniciar la UI
        if (
            AZURE_SPEECH_KEY == "PegaTuClaveAqui"
            or AZURE_SPEECH_REGION == "PegaTuRegionAqui"
            or not AZURE_SPEECH_KEY
            or not AZURE_SPEECH_REGION
        ):
            print(
                "❌ ERROR CRÍTICO: Debes configurar tu AZURE_SPEECH_KEY y AZURE_SPEECH_REGION.\n"
                "💡 Opciones:\n"
                "• Edita el archivo 'nexovoz_config.json' y cambia 'PegaTuClaveAqui' por tu clave real\n"
                "• O usa el botón de configuración (⚙️) en la interfaz\n"
                "• O edita directamente 'config.py'"
            )
            time.sleep(5)
            sys.exit(1)

        self.app = QApplication(sys.argv)

        # Establecer el icono de la aplicación
        icon_path = os.path.join(os.path.dirname(__file__), "icono_traductor.png")
        if os.path.exists(icon_path):
            self.app.setWindowIcon(QIcon(icon_path))

        self.main_window = VentanaSubtitulos()

        # Establecer el icono también en la ventana principal
        if os.path.exists(icon_path):
            self.main_window.setWindowIcon(QIcon(icon_path))

    def run(self):
        """Inicia el ciclo de la aplicación mostrando la ventana principal."""
        self.main_window.show()
        sys.exit(self.app.exec())


if __name__ == "__main__":
    # Iniciar la aplicación directamente con la ventana principal
    main_app = Application()
    main_app.run()
