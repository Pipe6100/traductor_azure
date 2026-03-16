🎙️ NexoVoz – Traductor de Voz en Tiempo Real con Azure

Sistema de traducción simultánea que captura audio desde un micrófono, lo transcribe y lo traduce en tiempo real utilizando Microsoft Azure Cognitive Services.

La aplicación permite generar subtítulos en vivo durante conferencias, clases, congresos o presentaciones multilingües.

📌 Proyecto personal

Este repositorio corresponde a un proyecto personal de desarrollo de software enfocado en la integración de:

Procesamiento de lenguaje natural

Reconocimiento de voz

Traducción automática

APIs de inteligencia artificial en la nube

El sistema busca reducir la barrera idiomática en eventos académicos y presentaciones internacionales.

👨‍💻 Autores

Walter Danilo Noguera Quintero
Ingeniería de Sistemas – Universidad de la Amazonia

Yeison Jhoan Cadena Córdoba
Ingeniería de Sistemas – Universidad de la Amazonia

Juan Felipe Loaiza Facundo
Ingeniería de Sistemas – Universidad de la Amazonia

Docente orientador:
Jesús Emilio Pinto Lopera

🎯 Objetivo del sistema

Ofrecer una herramienta de traducción simultánea asistida por inteligencia artificial para eventos, presentaciones o clases, generando subtítulos en vivo con baja latencia.

🌐 Tecnologías utilizadas

Este proyecto utiliza las siguientes tecnologías:

Python

Azure Cognitive Services

Azure Speech SDK

Azure Translator

Procesamiento de audio

Interfaz gráfica en Python

MongoDB (registro de datos)

☁️ APIs de Azure utilizadas

El sistema utiliza dos servicios principales de Microsoft Azure.

Azure Speech Service

Permite convertir audio a texto mediante reconocimiento de voz.

Azure Translator

Permite traducir automáticamente el texto reconocido a otros idiomas.

Flujo del sistema
Audio → Transcripción → Traducción → Subtítulos

```
📂 Estructura del proyecto
traductor_azure/
│
├── main.py
├── azure_worker.py
├── audio_config_ui.py
├── config.py
├── mongodb_service.py
├── styles.py
├── logger.py
├── ui.py
│
├── nexovoz_config.json
├── requirements.txt
│
├── CONFIGURACION_AUDIO_OMNIDIRECCIONAL.md
├── FUNCIONALIDAD_MULTI_IDIOMA.md
│
└── icono_traductor.png
```

⚙️ Requisitos

Para ejecutar la aplicación se requiere:

PC con mínimo 4 GB de RAM

Micrófono

Conexión a internet

Cuenta activa en Microsoft Azure

API de Speech y Translator habilitadas

⚙️ Instalación
Clonar el repositorio: git clone https://github.com/Pipe6100/traductor_azure.git

Entrar al proyecto
cd traductor_azure

Crear entorno virtual
python -m venv venv

Activar entorno
Windows

venv\Scripts\activate

Linux / Mac
source venv/bin/activate

Instalar dependencias
pip install -r requirements.txt

▶️ Ejecutar el proyecto
python main.py

```
🎤 Funcionalidades

El sistema permite:

✔ Reconocimiento de voz en tiempo real
✔ Traducción automática multilenguaje
✔ Subtítulos en vivo
✔ Configuración avanzada de audio
✔ Supresión de ruido
✔ Cancelación de eco
✔ Control automático de ganancia
✔ Ajuste de sensibilidad del micrófono
```

🎬 Casos de uso

Este sistema puede utilizarse en:

Congresos académicos

Conferencias internacionales

Clases bilingües

Eventos multilingües

Presentaciones con subtítulos en vivo

🔐 Seguridad

Se recomienda:

No subir al repositorio las API Keys de Azure Cognitive Services.

Estas claves corresponden a los servicios utilizados por la aplicación:

Azure Speech Service (reconocimiento de voz)

Azure Translator Service (traducción automática)

Almacenar las credenciales mediante variables de entorno o archivos de configuración locales excluidos del control de versiones.

```
Ejemplo de variables de entorno
AZURE_SPEECH_KEY
AZURE_SPEECH_REGION
AZURE_TRANSLATOR_KEY
AZURE_TRANSLATOR_REGION
```

📜 Licencia

Proyecto académico y de demostración.

# 📄 Documentación

Este repositorio incluye:

- 📘 [Manual Técnico](https://docs.google.com/document/d/1eeRgAkRW4Ri2wKqOIiRjO0gnj73C_nZt/edit?usp=drive_link&ouid=109601953445273230093&rtpof=true&sd=true)
- 📗 [Manual de Usuario](https://docs.google.com/document/d/1s3w4PvfknODNDu3h8kxtNhJcEFrDR7Pr/edit?usp=drive_link&ouid=109601953445273230093&rtpof=true&sd=true)

🧠 Arquitectura del sistema

El sistema sigue una arquitectura modular orientada a eventos, separando las responsabilidades de captura de audio, procesamiento de voz, traducción y visualización.

```
Flujo interno del sistema

Micrófono
   ↓
Captura de audio
   ↓
Azure Speech Service
   ↓
Transcripción a texto
   ↓
Azure Translator
   ↓
Texto traducido
   ↓
Interfaz gráfica
   ↓
Subtítulos en vivo
```

```
Componentes principales

Captura de audio
Obtiene el audio desde el micrófono.

Motor de reconocimiento
Azure Speech convierte voz a texto.

Motor de traducción
Azure Translator traduce el texto detectado.

Interfaz gráfica
Muestra los subtítulos en tiempo real.

Registro de datos
MongoDB almacena información de uso.
```

⚡ Rendimiento

El sistema está diseñado para operar con baja latencia, permitiendo que la traducción aparezca casi en tiempo real.

Factores que influyen en el rendimiento

Calidad del micrófono

Velocidad de conexión a internet

Latencia de los servicios de Azure

Nivel de ruido en el entorno

En condiciones normales, la traducción aparece entre 1 y 3 segundos después de la pronunciación.

🔧 Posibles mejoras futuras

El proyecto puede ampliarse con nuevas funcionalidades como:

Traducción a más idiomas simultáneamente

Síntesis de voz para reproducir la traducción

Exportación automática de transcripciones

Soporte para múltiples micrófonos

Modo conferencia multicanal

Interfaz web para uso remoto

Integración con Zoom / Teams / Meet

📊 Aplicaciones potenciales

La tecnología implementada en este proyecto puede aplicarse en distintos contextos:

Educación internacional

Conferencias científicas

Eventos empresariales

Turismo

Accesibilidad para personas con dificultades auditivas

Comunicación intercultural en tiempo real

⭐ Reconocimientos

Este proyecto fue desarrollado como ejercicio académico y de investigación en el área de:

Inteligencia Artificial aplicada

Procesamiento de lenguaje natural

Reconocimiento de voz

Sistemas de traducción automática

Utilizando los servicios de Microsoft Azure Cognitive Services.