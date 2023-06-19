#!/bin/bash


abspath=$(dirname $(dirname $(pwd)))

# Ce script lance un serveur OCSP écoutant sur le port 8080.


# Installer les paquets nécessaires
sudo apt update
sudo apt full-upgrade -y
sudo apt autoremove -y
sudo apt install openssl

# Générer une clé privée et un certificat de demande de signature de certificat (CSR) pour le serveur OCSP
openssl genrsa -out ocsp.key 4096
openssl req -new -key ocsp.key -out ocsp.csr

# Obtenir un certificat signé par une autorité de certification (CA) pour le serveur OCSP à partir de la CSR générée à l étape précédente. Vous pouvez également utiliser un certificat auto-signé pour des tests internes. Pour générer un certificat auto-signé :
openssl x509 -req -in ocsp.csr -CA $abspath/ACI/aci_cert.pem -CAkey $abspath/ACI/aci_key.pem -CAcreateserial -out ocsp.crt -days 30

# Créer un fichier de configuration OCSP (ocsp.conf) avec le contenu suivant
touch ocsp.conf

echo "[ocsp]
dir = $abspath/code/OCSP
certs = \$dir
[req]
distinguished_name = req_distinguished_name
[req_distinguished_name]
commonName = OCSP Responder
[ocsp_extensions]
basicConstraints = CA:false
keyUsage = nonRepudiation, digitalSignature, keyEncipherment
extendedKeyUsage = OCSPSigning
" > ocsp.conf

# Mettre à jour le certificat OCSP avec les extensions nécessaires en utilisant le fichier de configuration
openssl x509 -req -in ocsp.csr -signkey ocsp.key -out ocsp.crt -days 30 -extfile ocsp.conf -extensions ocsp_extensions

# Télécharger les certificats de l'autorité de certification (CA) et de la CA intermédiaire (si applicable) et placez-les dans le répertoire OCSP créé précédemment. Par exemple :
cp ../../ACR/acr_cert.pem ./root_ca.crt
cp ../../ACI/aci_cert.pem ./intermediate_ca.crt

# Créer un fichier index pour la base de données OCSP :
touch index.txt

# Démarrer le serveur OCSP avec OpenSSL
openssl ocsp -index index.txt -port 8080 -rsigner ocsp.crt -rkey ocsp.key -CA root_ca.crt -text
