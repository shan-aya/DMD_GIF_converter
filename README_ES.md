[🇫🇷 Français](./README.md) · [🇬🇧 English](./README_EN.md) · 🇪🇸 **Español**

DMD GIF Creator 128x32 - v3.0
Shan_ayA 2026

Aplicación completa para crear GIF optimizados para pantallas DMD 128x32: a partir de
imágenes (análisis automático y propuestas), de un vídeo o de texto animado, con
edición manual avanzada.

(Antes « DMD GIF Converter ».)

## Novedades de la v3.0

- **Pestaña VIDEO**: convierte un fragmento de vídeo (MP4, AVI, MOV, MKV) en un GIF
  128×32, con selección del fragmento, encuadre por seguimiento automático, encuadre
  automático o puntos manuales (zona y zoom que evolucionan en el tiempo) y calidad
  automática.
- **Pestaña AYUDA**: la guía completa dentro de la aplicación, en francés, inglés o
  español.
- **Arrastrar y soltar** imágenes, carpetas o un vídeo en cualquier lugar de la
  ventana.
- **Vista previa LED** fiel al render del panel (lupa, brillo LED) en todas las
  pestañas de creación.
- **Procesamiento por lotes en paralelo**, y carpetas muy grandes (decenas de miles de
  imágenes) cargadas en unos segundos sin congelar la ventana.
- Formato **raw565** aceptado como entrada, historial deshacer/rehacer en la pestaña
  MANUAL, ayudas emergentes, traducciones FR/EN/ES revisadas.

Detalle (en francés): [CHANGELOG_FR](./CHANGELOG_FR)

## Instalación

**Windows**: descargue `dmd_gif_creator_v300.exe` desde la
[última Release](https://github.com/shan-aya/DMD_GIF_converter/releases/latest) y
ejecútelo — no hace falta instalar nada.

**Desde las fuentes** (carpeta [`dmd_gif_creator/`](./dmd_gif_creator)):

    pip install pillow numpy tkinterdnd2 markdown opencv-contrib-python
    python dmd_gif_creator/dmd_gif_creator_v300.py

`opencv-contrib-python` (y no `opencv-python`) es necesario para el seguimiento
automático de la pestaña VIDEO; los dos paquetes no deben instalarse a la vez.

## Capturas (versión 2.7)

<img width="1909" height="1079" alt="Captura 2026-04-29 150630" src="https://github.com/user-attachments/assets/5515fd66-c5e9-4370-939c-48becf656cae" />
<img width="1909" height="1079" alt="Captura 2026-04-29 150638" src="https://github.com/user-attachments/assets/c6892979-22fd-4854-8c5b-2cb591af6243" />
<img width="1909" height="1079" alt="Captura 2026-04-29 150929" src="https://github.com/user-attachments/assets/bd582c2c-f7c8-48e3-a1a3-f77a23da3d75" />
<img width="1908" height="1077" alt="Captura 2026-04-29 150940" src="https://github.com/user-attachments/assets/d43e075e-7286-4e7f-a94e-2866367303f7" />


## Documentación

La guía completa está disponible aquí:

- [Version Française 🇫🇷](./NOTICE_FR.md)
- [Versión en Español 🇪🇸](./NOTICE_ES.md)
- [Version in english EN](./NOTICE_EN.md)

Haga clic en el idioma deseado para abrir la guía correspondiente. La misma guía está
disponible dentro de la aplicación, pestaña **AYUDA**.


---

## 🤝 Agradecimientos

- [RetroPixelLED original](https://github.com/fjgordillo86/RetroPixelLED)
- Visual Studio Code
- [Sixth](https://trysixth.com/)

## ☕ Apoyar el proyecto

Si este proyecto te ha ayudado, puedes invitarme a un café:

👉 [☕ Donate via PayPal](https://www.paypal.com/paypalme/felysaya)

## Contacto

Para cualquier pregunta, sugerencia o contribución, abra un issue o contacte con el autor Shan_ayA.

---

© 2026 Shan_ayA
