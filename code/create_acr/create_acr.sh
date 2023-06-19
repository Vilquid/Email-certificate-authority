#!/bin/bash


# Le script génère un répertoire ACR contenant la clé privée de l'ACR (acr_key.pem) et son certificat auto-signé (acr_cert.pem), ainsi qu'un fichier de configuration OpenSSL (acr_openssl.cnf).

# Variables
ACR_NAME="ACR"
ACR_KEY="acr_key.pem"
ACR_CERT="acr_cert.pem"
ACR_CONF="acr_openssl.cnf"

# Création du répertoire de l'ACR
mkdir -p "${ACR_NAME}"
cd "${ACR_NAME}"

# Génération de la clé privée de l'ACR
openssl genpkey -algorithm EC -out "${ACR_KEY}" -pkeyopt ec_paramgen_curve:P-521 -pkeyopt ec_param_enc:named_curve

# Configuration OpenSSL pour l'ACR
cat > "${ACR_CONF}" <<- EOM
[ req ]
default_bits        = 521
prompt              = no
default_md          = sha512
distinguished_name  = dn

[ dn ]
C  = FR
ST = Var
L  = Toulon
O  = ISEN
OU = ISEN
CN = ACR

[ v3_ca ]
subjectKeyIdentifier   = hash
authorityKeyIdentifier = keyid:always,issuer
basicConstraints       = CA:true
keyUsage               = digitalSignature, cRLSign, keyCertSign
EOM

# Génération du certificat auto-signé de l'ACR
openssl req -x509 -new -nodes -key "${ACR_KEY}" -days 3000 -out "${ACR_CERT}" -config "${ACR_CONF}" -extensions v3_ca

echo "L'ACR et son certificat auto-signé ont été créés."
