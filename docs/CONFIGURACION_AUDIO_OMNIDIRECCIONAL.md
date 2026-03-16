# Configuración de Audio Omnidireccional - NexoVoz

## Descripción

Esta guía explica cómo configurar tu micrófono para que actúe de manera más omnidireccional y capture el ruido de todos los lados en la aplicación NexoVoz.

## ¿Qué es la Captura Omnidireccional?

La captura omnidireccional permite que tu micrófono detecte y capture sonidos provenientes de todas las direcciones (360 grados), no solo desde una dirección específica. Esto es especialmente útil para:

- Reuniones con múltiples personas
- Entornos donde el hablante puede moverse
- Captura de audio ambiental
- Mejores traducciones en espacios amplios

## Configuración en NexoVoz

### 1. Acceder a la Configuración de Audio

1. Abre la aplicación NexoVoz
2. En la ventana principal, haz clic en el botón **🎤** (verde) junto al botón de configuración
3. Se abrirá el diálogo "Configuración de Audio - Captura Omnidireccional"

### 2. Configuraciones Disponibles

#### Configuración Básica
- **Frecuencia de muestreo**: 8000, 16000, 22050, 44100, 48000 Hz
- **Tamaño de chunk**: 256-4096 (recomendado: 1024)

#### Procesamiento de Audio
- **Habilitar procesamiento de audio**: Activa/desactiva el procesamiento
- **Supresión de ruido**: 
  - `off`: Sin supresión
  - `moderate`: Supresión moderada (recomendado)
  - `aggressive`: Supresión agresiva
- **Cancelación de eco**: Elimina el eco del audio
- **Control automático de ganancia**: Ajusta automáticamente el volumen

#### Sensibilidad del Micrófono
- **Sensibilidad**: 
  - `low`: Baja sensibilidad
  - `medium`: Sensibilidad media
  - `high`: Alta sensibilidad (recomendado para omnidireccional)
- **Boost de audio**: Amplifica la señal de audio

#### Configuración de Azure Speech SDK
- **Timeout de silencio**: 100-5000 ms (recomendado: 500)
- **Tiempo máximo de segmentación**: 10000-70000 ms (recomendado: 20000)
- **Filtro de profanidad**: raw, masked, removed
- **Logging de audio**: Activa/desactiva el registro de audio

### 3. Configuración Recomendada para Omnidireccional

Para obtener la mejor captura omnidireccional, usa estas configuraciones:

```
Configuración Básica:
- Frecuencia de muestreo: 16000 Hz
- Tamaño de chunk: 1024

Procesamiento de Audio:
✅ Habilitar procesamiento de audio
- Supresión de ruido: moderate
✅ Cancelación de eco
✅ Control automático de ganancia

Sensibilidad:
- Sensibilidad: high
✅ Boost de audio

Azure Speech SDK:
- Timeout de silencio: 500 ms
- Tiempo máximo: 20000 ms
- Filtro de profanidad: masked
❌ Logging de audio (opcional)
```

### 4. Aplicar Configuración

1. Ajusta las configuraciones según tus necesidades
2. Haz clic en **"Guardar"**
3. La configuración se aplicará automáticamente
4. Si tienes una sesión de traducción activa, se reiniciará con las nuevas configuraciones

## Limitaciones del Hardware

**Importante**: La configuración de software puede mejorar la captura, pero las limitaciones físicas del micrófono son determinantes:

### Micrófonos Omnidireccionales Verdaderos
- Capturan sonido de 360 grados uniformemente
- Ideales para reuniones y espacios amplios
- Pueden capturar más ruido ambiental

### Micrófonos Direccionales
- Capturan principalmente desde una dirección
- No se pueden hacer verdaderamente omnidireccionales con software
- La configuración de alta sensibilidad puede ayudar, pero con limitaciones

### Micrófonos de Direccionalidad Variable
- Permiten cambiar el patrón polar físicamente
- Pueden configurarse en modo omnidireccional
- Son la mejor opción para flexibilidad

## Consejos para Mejorar la Captura

1. **Posicionamiento**: Coloca el micrófono en el centro del área de conversación
2. **Altura**: A la altura de las bocas de los hablantes
3. **Distancia**: No demasiado cerca ni demasiado lejos
4. **Entorno**: Minimiza el ruido de fondo cuando sea posible
5. **Pruebas**: Prueba diferentes configuraciones según tu entorno

## Solución de Problemas

### Si no captura bien desde todos los lados:
1. Verifica que tu micrófono sea omnidireccional
2. Aumenta la sensibilidad a "high"
3. Activa el "Boost de audio"
4. Ajusta el timeout de silencio a 300-500 ms

### Si captura demasiado ruido:
1. Reduce la sensibilidad a "medium"
2. Activa la supresión de ruido "aggressive"
3. Desactiva el "Boost de audio"
4. Mejora el entorno acústico

### Si hay eco o feedback:
1. Activa la "Cancelación de eco"
2. Reduce la sensibilidad
3. Ajusta la posición del micrófono

## Notas Técnicas

- Las configuraciones se guardan en `nexovoz_config.json`
- Los cambios se aplican inmediatamente si hay una sesión activa
- La configuración se mantiene entre sesiones de la aplicación
- Para restablecer a valores por defecto, usa el botón "Restaurar por defecto"

## Soporte

Si tienes problemas con la configuración de audio, verifica:
1. Que tu micrófono esté funcionando correctamente
2. Que los permisos de micrófono estén habilitados
3. Que no haya otras aplicaciones usando el micrófono
4. Que las credenciales de Azure estén configuradas correctamente

