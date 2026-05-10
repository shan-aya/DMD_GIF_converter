# Manual de Usuario - DMD GIF Converter 128x32 v2.7

## Índice
- [Pestaña AUTO 🤖](#pestaña-auto-🤖)
- [Pestaña MANUAL ✍️](#pestaña-manual-✍️)
- [Pestaña TEXTSCROLL 📝](#pestaña-textscroll-📝)
- [Pestaña AJUSTES ⚙️](#pestaña-ajustes-⚙️)
- [Pestaña DEBUG 🐞](#pestaña-debug-🐞)

---

## Pestaña AUTO 🤖

### Presentación  
La pestaña **AUTO** permite la conversión automática de imágenes a GIF optimizados para pantalla DMD 128x32, con ajustes globales y propuestas generadas por un motor IA.

### Funcionalidades

- 📁 **Seleccionar carpeta**: Elige una carpeta fuente que contenga imágenes.  
- 🖼️ **Seleccionar imágenes**: Selección manual de imágenes a convertir.  
- ✔️ **Recursivo**: Incluir subcarpetas al seleccionar.  
- ⚙️ **Parámetros globales**:
  - FPS (imágenes/segundo) ⏱️  
  - Duración mínima en segundos ⌛  
  - Velocidad del scroll (píxeles por frame) 🌀  
  - Contraste, Saturación y número de colores para GIF 🎨  

- 🖼️ **Lista de imágenes** con opciones para seleccionar todo, nada o invertir la selección.  
- 🔓 **Reautorizar imagen** para reactivar el procesamiento de imágenes excluidas en modo MANUAL.  
- 💻 **Vista previa** de la imagen original y la versión DMD 128x32.  
- 💡 **Propuestas IA** mostradas como miniaturas con opción a bloqueo.  
- 🚀 **Botones**:
  - Procesar todas las imágenes de la carpeta o la selección  
  - Procesar solo las imágenes seleccionadas

### Sugerencias  
- Selecciona tu carpeta o imágenes y presiona “Procesar todo” para generar automáticamente las versiones optimizadas según el motor comparativo.  
- Bloquea una propuesta IA para aplicarla a todas las imágenes (excluyendo el motor comparativo).  
- Si seleccionas una imagen y cambias a la pestaña MANUAL, esta aparecerá automáticamente y saldrá del procesamiento automático al generar un archivo GIF.

---

## Pestaña MANUAL ✍️

### Presentación  
La pestaña **MANUAL** ofrece herramientas avanzadas para editar imágenes manualmente, aplicar efectos y crear animaciones personalizadas.

### Funcionalidades principales

- 📂 **Cargar imagen** para edición manual.  
- ✂️ **Recortar 128×32**: Definir un área de recorte precisa.  
- ↶ **Deshacer**: Permite revertir la última modificación (historial guardado).  
- 💾 **Exportar GIF**: Guardar el trabajo realizado.  
- 📚 **Multi-imágenes**: Cargar hasta 4 imágenes para animaciones morphing.  
- 🎬 **Morphing**: Generar animaciones de transición entre esas imágenes.

### Efectos en tiempo real 🖌️

- Ajustes mediante sliders: brillo, contraste, saturación, nitidez.  
- Filtros populares: desenfoque, gaussiano, contornos, relieve, detalles+, invertir, espejo horizontal/vertical, rotar 90°, blanco&negro, solarizar, posterizar, ecualizar, auto-contraste.  
- Herramientas de dibujo: relleno 🎨 y goma mágica 🧹 con selección de color y tolerancia.

### Animación y parámetros

- Selección de animación: scroll, fade, zoom, rotación, ola, rebote, flash, deslizamiento, espiral, temblor, pulso, glitch, pixelado, transición borrosa, cambio de color.  
- Configuración de FPS, velocidad, duración, tipo de bucle (normal, ping-pong, infinito) y repeticiones.  
- Controles avanzados: easing, retardo inicial, invertir dirección, opacidad.

### Vista previa

- Visualización en vivo de la animación en el panel derecho.  
- Estado e información detallada de la imagen.

---

## Pestaña TEXTSCROLL 📝

### Presentación  
Permite crear y animar textos desplazándose, optimizados para DMD 128x32.

### Funcionalidades

- 📝 **Área de texto** para introducir el contenido (sin límite).  
- 👩‍🎨 **Personalización de fuente**:
  - Familia (lista completa de fuentes del sistema)  
  - Tamaño  
  - Estilos Negrita, Cursiva  
  - Color de texto y fondo mediante selectores de color.  
- 🎨 **Efectos visuales para texto**:
  - Normal, 3D, fuego, nieve, hielo, metal, neón, graffiti, pixel art, contorno, sombra.  
- 🌈 **Efectos de color**:
  - Arcoíris, matrix, fuego, degradado, ninguno.  
- 🔄 **Animaciones de texto**:
  - Scroll horizontal/vertical, scroll con onda, estilo Star Wars, rebote, máquina de escribir, explosión, lluvia Matrix, espiral, temblor, glitch, fundido, estático.  
- ⏱️ **Ajustes de animación**:
  - FPS, velocidad, duración  
  - Opción de auto-ajuste.

### Controles

- 🎬 **Generar vista previa** de la animación.  
- 💾 **Exportar GIF** para guardar la animación de texto.

---

## Pestaña AJUSTES ⚙️

### Configuración global de la aplicación

- 🌍 **Idioma**: Francés 🇫🇷, Inglés 🇬🇧, Español 🇪🇸.  
- 🎨 **Apariencia**: Tema oscuro (por defecto) o claro.  
- ⚙️ **Comportamiento**:
  - Opción para añadir tipo de animación al nombre del archivo exportado.  
- 🎨 **Calidad de exportación GIF**: Número de colores predeterminado [8,16,32,64,128,256].  
- ⚡ **Rendimiento**: Activación/desactivación de la caché IA.  
- 🗑️ **Caché**: Botón para vaciar la caché.  
- 📜 **Logs**: Opciones para guardar, exportar o borrar los registros de actividad.

---

## Pestaña DEBUG 🐞

### Herramientas para desarrolladores y depuración

- 🗑️ **Borrar logs**.  
- ✅ **Auto-scroll** de registros.  
- 🔍 **Filtrar logs** por nivel: TODO, INFO, ADVERTENCIA, ERROR, DEBUG.  
- 📝 Visualización en tiempo real con colores según nivel.

---

# Navegación entre idiomas

Para cambiar al manual en francés, haz clic aquí:  
[Leer en Français 🇫🇷](./NOTICE_FR.md)

---

# Resumen

Este manual te guía en el uso de cada pestaña del DMD GIF Converter 128x32. Usa AUTO para conversiones rápidas, MANUAL para edición avanzada, TEXTSCROLL para crear textos animados, AJUSTES para configuración global y DEBUG para diagnóstico y seguimiento.

✨ Para comenzar, carga imágenes, prueba efectos y exporta tus GIFs optimizados. Consulta DEBUG en caso de problemas.
