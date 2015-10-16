# nxpush

## Description


Ce module écrit en python s'appuie sur le client écrit par sfermigier pour la partie rest (imports des documents réceptionnés dans la ged)

Le client original a subi quelques modifications pour utiliser base64 et rendre possible l'importation des binaires qui fonctionnait de manière aléatoire voire pas du tout dans l'état original de la librairie. Il faut donc utiliser le client inclus dans le module.

Le module s'appuie également sur pyinotify pour la partie monitoring du système de fichier. Comme les scans intègrent déjà une fonctionnalité de suppression des fichiers numérisés après un nombre de jour défini le seul gestionnaire d'événements qui a été créé réponds aux événements de type création de fichier.

## Principe de fonctionnement :


 - Le scanner est configuré pour numériser dans un répertoire défini.
 - Le service est à l'écoute des événements de type création de fichier pour ce répertoire (défini dans sa configuration).
 - La création d'un fichier dans le répertoire provoque:
  - L'exécution d'un script qui procède à une reconnaissance optique de caractères sur le document
  - L'envoi du fichier dans la ged dans à l'endroit défini dans la configuration du service ( via http )
 - Le fichier n'est pas supprimé à l'issue du processus

Installation
Globalement  il faut placer le module sur la machine qui reçoit les scans et lancer le fichier nxpush.py.

Les prérequis sont python 2.7 et pyinotify + tesseract pour le module d'OCR

Installation de pyinotify (debian)

apt-get install python-pip python-dev build-essential
pip install --upgrade pip 
pip install setuptools --no-use-wheel –upgrade
pip install pyinotify

Installer tesseract. La version qui fonctionne à l'heure ou est rédigé ce document est la suivante.

tesseract 3.03 
 leptonica-1.70 
  libgif 4.1.6(?) : libjpeg 8d : libpng 1.2.50 : libtiff 4.0.3 : zlib 1.2.8 : webp 0.4.0 

Un script de démarrage sommaire qui a servi en phase de développement est inclus dans le module. 

Avant de lancer le module il faut configurer les options d'authentification et de mapping entre la GED et le système de fichiers local. 


## Configuration


La configuration du mapping s'effectue dans le fichier nx-properties.xml qui DOIT se trouver dans le même répertoire que le fichier nxpush.py

La partie credentials contient le chemin vers le fichier contenant les identifiants utilisés par le service
La partie mapper contient uune balise mapping avec
Une partie local qui indique le répertoire à l'écoute sur le système de fichier
Une partie remote qui indique le répertoire destinataire des documents dans la ged
Les balises mapping peuvent être multipliées pour mettre plusieurs répertoire à l'écoute.

Il suffit ensuite de créer le fichier credentials.xml avec des droits restreints et de lui donner la forme suivante :

```xml
<?xml version="1.0"?> 

<credentials> 
        <user>${username}</user> 
        <pass>${password}</pass> 
</credentials> 
```

## Exécution


Une fois la configuration faite il suffit de lancer le service. Le scanner doit être configuré pour numériser au bon endroit. Toutes les opérations de routage de documents sont implémentées côté GED.
