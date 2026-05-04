# Notice d'Utilisation - DMD GIF Converter 128x32 v2.0

## Sommaire
- [Onglet AUTO 🤖](#onglet-auto-🤖)
- [Onglet MANUEL ✍️](#onglet-manuel-✍️)
- [Onglet TEXTSCROLL 📝](#onglet-textscroll-📝)
- [Onglet PARAMÈTRES ⚙️](#onglet-paramètres-⚙️)
- [Onglet DEBUG 🐞](#onglet-debug-🐞)

---

## Onglet AUTO 🤖

### Présentation
L'onglet **AUTO** permet la conversion automatique d'images en GIF optimisés pour écran DMD 128x32, avec des réglages globaux et des propositions générées par un moteur IA.

### Fonctionnalités

- 📁 **Sélection dossier** : Choisir un dossier source contenant des images.
- 🖼️ **Sélection images** : Choisir manuellement des images à convertir.
- ✔️ **Récursif** : Inclure les sous-dossiers lors de la sélection.
- ⚙️ **Paramètres globaux** :
  - FPS (images/seconde) ⏱️
  - Durée de l'animation en secondes ⌛
  - Vitesse du scroll (pixels/frame) 🌀
  - Contraste, Saturation et nombre de couleurs GIF 🎨

- 🖼️ **Liste des images** affichée avec possibilité de sélectionner, tout cocher/décocher, inverser la sélection.
- 🔓 **Réautoriser une image** pour rafraîchir le traitement.
- 💻 **Prévisualisation** de l'image originale et du rendu DMD 128x32.
- 💡 **Propositions IA** : Affichées sous forme de miniatures avec verrouillage possible.
- 🚀 **Boutons** :
  - Traiter tout le dossier/images sélectionnées
  - Traiter uniquement les images sélectionnées

### Astuces
- Sélectionnez vos images puis cliquez sur "Traiter tout" pour générer automatiquement les versions optimisées.
- Verrouillez une proposition IA pour la sauvegarder sans qu'elle soit écrasée lors d'autres opérations.

---

## Onglet MANUEL ✍️

### Présentation
L'onglet **MANUEL** offre des outils avancés d'édition manuelle des images, avec application d'effets et animation personnalisée.

### Fonctionnalités principales

- 📂 **Charger une image** pour édition manuelle.
- ✂️ **Crop 128×32** : Définir une zone de recadrage ciblée.
- ↶ **Annuler** : Permet d'annuler la dernière modification.
- 💾 **Exporter GIF** : Sauvegarder le travail.
- 📚 **Multi-images** : Charger plusieurs images pour animations morphing.
- 🎬 **Morphing** : Générer une animation de transition entre plusieurs images.

### Effets temps réel 🖌️

- Luminosité, Contraste, Saturation, Netteté (sliders).
- Filtres populaires : Flou, Gaussien, Contours, Relief, Détails+, inverser, miroir, rotation, noir&blanc, solariser, posteriser, égaliser, auto-contraste.
- Outils dessin : Remplissage 🎨 et gomme magique 🧹 avec choix couleur et tolérance.

### Animation & Paramètres

- Choix du type d'animation (scroll, fade, zoom, rotation, vagues, rebond, flash, glissement, spirale, tremblement, pulsation, glitch, pixelisation, transition floue, décalage couleur).
- Réglage FPS, vitesse, durée, type de boucle (normal, ping-pong, infini), répétitions.
- Contrôles avancés : easing, délai début, inversion, opacité.

### Aperçu

- Visualisation live de l'animation dans le panneau de droite.
- Statut et informations détaillées de l'image.

---

## Onglet TEXTSCROLL 📝

### Présentation
Permet la création et animation de texte défilant optimisé pour DMD 128x32.

### Fonctionnalités

- 📝 **Zone de texte** pour saisir le contenu à afficher.
- 👩‍🎨 **Personnalisation police** :
  - Famille (liste complète des polices système)
  - Taille
  - Style Gras, Italique
  - Couleur de texte et de fond (via sélecteurs de couleur)
- 🎨 **Effets visuels sur texte** :
  - Normal, 3D, feu, neige, glace, métal, néon, graffiti, pixel art, outline, ombre
- 🌈 **Effets de couleur** :
  - Arc-en-ciel, matrix, feu, dégradé, aucun
- 🔄 **Animations de texte** :
  - Scroll horizontal/vertical, scroll vague, style Star Wars, rebonds, machine à écrire, explosion, pluie Matrix, spirale, tremblement, glitch, fondu, statique
- ⏱️ **Réglages animation** :
  - FPS, vitesse, durée
  - Option auto-ajustement

### Contrôles

- 🎬 **Générer Preview** : Affiche l’animation générée.
- 💾 **Exporter GIF** : Sauvegarder l’animation texte.

---

## Onglet PARAMÈTRES ⚙️

### Configuration globale de l’application

- 🌍 **Langue** : Français 🇫🇷, English 🇬🇧, Español 🇪🇸.
- 🎨 **Apparence** : Thème sombre (par défaut) ou clair.
- ⚙️ **Comportement** :
  - Option pour ajouter le type d'animation au nom de fichier exporté.
- 🎨 **Qualité export GIF** : Nombre de couleurs par défaut [8,16,32,64,128,256].
- ⚡ **Performance** : Activation/désactivation cache IA.
- 🗑️ **Cache** : Bouton pour vider le cache.
- 📜 **Logs** : Options pour sauvegarder, exporter ou effacer les journaux d’activité.

---

## Onglet DEBUG 🐞

### Outils pour développeurs et dépannage

- 🗑️ **Effacer logs**.
- ✅ **Auto-scroll** des logs.
- 🔍 **Filtrer logs** par niveau : ALL, INFO, WARNING, ERROR, DEBUG.
- 📝 Affichage en temps réel des logs avec coloration syntaxique selon le niveau.

---

# Navigation entre langues

Pour passer à la version espagnole, cliquez ici :  
[Leer en Español 🇪🇸](./NOTICE_ES.md)

---

# Résumé

Cette notice vous guide dans l’utilisation de chaque onglet du DMD GIF Converter 128x32. Utilisez AUTO pour la conversion rapide, MANUEL pour l’édition avancée, TEXTSCROLL pour créer des textes animés, PARAMÈTRES pour la configuration globale, et DEBUG pour dépannage et suivi.

✨ Pour démarrer, chargez des images, testez les effets et exportez vos GIFs optimisés. Consultez DEBUG en cas de problème.
