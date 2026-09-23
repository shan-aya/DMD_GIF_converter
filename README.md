🇫🇷 **Français** · [🇬🇧 English](./README_EN.md) · [🇪🇸 Español](./README_ES.md)

DMD GIF Creator 128x32 - v3.0
Shan_ayA 2026

Application complète de création de GIF optimisés pour écrans DMD 128x32 : à partir
d'images (analyse automatique et propositions), d'une vidéo, ou de texte animé, avec
édition manuelle avancée.

(Anciennement « DMD GIF Converter ».)

## Nouveautés de la v3.0

- **Onglet VIDEO** : un passage de vidéo (MP4, AVI, MOV, MKV) transformé en GIF 128×32,
  avec sélection du passage, cadrage par suivi automatique, cadrage auto ou points
  manuels (zone et zoom qui évoluent dans le temps), qualité automatique.
- **Onglet AIDE** : le guide complet dans l'application, en français, anglais ou
  espagnol.
- **Glisser-déposer** d'images, de dossiers ou d'une vidéo n'importe où dans la
  fenêtre.
- **Aperçu LED** fidèle au rendu du panneau (loupe, réglage de luminosité) dans tous
  les onglets de création.
- **Traitement par lot en parallèle**, et chargement de très gros dossiers (plusieurs
  dizaines de milliers d'images) en quelques secondes sans figer la fenêtre.
- Format **raw565** accepté en entrée, historique annuler/rétablir dans l'onglet
  MANUEL, infobulles d'aide, traductions FR/EN/ES revues.

Détail : [CHANGELOG_FR](./CHANGELOG_FR)

## Installation

**Windows** : téléchargez `dmd_gif_creator_v300.exe` dans la
[dernière Release](https://github.com/shan-aya/DMD_GIF_converter/releases/latest) et
lancez-le — aucune installation nécessaire.

**Depuis les sources** (dossier [`dmd_gif_creator/`](./dmd_gif_creator)) :

    pip install pillow numpy tkinterdnd2 markdown opencv-contrib-python
    python dmd_gif_creator/dmd_gif_creator_v300.py

`opencv-contrib-python` (et non `opencv-python`) est nécessaire pour le suivi
automatique de l'onglet VIDEO ; les deux paquets ne doivent pas être installés en même
temps.

## Captures (version 2.7)

<img width="1909" height="1079" alt="Capture d&#39;écran 2026-04-29 150630" src="https://github.com/user-attachments/assets/5515fd66-c5e9-4370-939c-48becf656cae" />
<img width="1909" height="1079" alt="Capture d&#39;écran 2026-04-29 150638" src="https://github.com/user-attachments/assets/c6892979-22fd-4854-8c5b-2cb591af6243" />
<img width="1909" height="1079" alt="Capture d&#39;écran 2026-04-29 150929" src="https://github.com/user-attachments/assets/bd582c2c-f7c8-48e3-a1a3-f77a23da3d75" />
<img width="1908" height="1077" alt="Capture d&#39;écran 2026-04-29 150940" src="https://github.com/user-attachments/assets/d43e075e-7286-4e7f-a94e-2866367303f7" />


## Documentation

Vous pouvez consulter la notice complète ici :

- [Version Française 🇫🇷](./NOTICE_FR.md)  
- [Versión en Español 🇪🇸](./NOTICE_ES.md)
- [Version in english EN](./NOTICE_EN.md) 

Cliquez sur la langue souhaitée pour accéder à la documentation correspondante. La
même notice est disponible dans l'application, onglet **AIDE**.


---

## 🤝 Remerciements

- [RetroPixelLED original](https://github.com/fjgordillo86/RetroPixelLED)
- Visual Studio Code
- [Sixth](https://trysixth.com/)

## ☕ Soutenir le projet

Si ce projet t’as aidé, tu peux m’offrir un café :

👉 [☕ Donate via PayPal](https://www.paypal.com/paypalme/felysaya)

## Contact

Pour toute question, suggestion ou contribution, créez un issue ou contactez l’auteur Shan_ayA.

---

© 2026 Shan_ayA
