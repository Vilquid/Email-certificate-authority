#!/bin/bash


# Le script génère un répertoire ACI contenant la clé privée de l'ACI (aci_key.pem), la CSR de l'ACI (aci_csr.pem) et son certificat signé par l'ACR (aci_cert.pem), ainsi qu'un fichier de configuration OpenSSL (aci_openssl.cnf).

# Variables
ACI_NAME="ACI"
ACI_KEY="aci_key.pem"
ACI_CSR="aci_csr.pem"
ACI_CERT="aci_cert.pem"
ACI_CONF="aci_openssl.cnf"

# Répertoires et fichiers de l'ACR
ACR_NAME="ACR"
ACR_KEY="../${ACR_NAME}/acr_key.pem"
ACR_CERT="../${ACR_NAME}/acr_cert.pem"
ACR_CONF="../${ACR_NAME}/acr_openssl.cnf"

# Création du répertoire de l'ACI
mkdir -p "${ACI_NAME}"
cd "${ACI_NAME}"

# Génération de la clé privée de l'ACI
openssl genpkey -algorithm EC -out "${ACI_KEY}" -pkeyopt ec_paramgen_curve:P-521 -pkeyopt ec_param_enc:named_curve

# Configuration OpenSSL pour l'ACI
cat > "${ACI_CONF}" <<- EOM
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
CN = ACI

[ v3_ca ]
subjectKeyIdentifier   = hash
authorityKeyIdentifier = keyid:always,issuer
basicConstraints       = CA:true
keyUsage               = digitalSignature, cRLSign, keyCertSign
EOM

# Génération de la CSR pour l'ACI
openssl req -new -key "${ACI_KEY}" -out "${ACI_CSR}" -config "${ACI_CONF}"

# Signature du certificat de l'ACI par l'ACR
openssl x509 -req -in "${ACI_CSR}" -CA "${ACR_CERT}" -CAkey "${ACR_KEY}" -CAcreateserial -out "${ACI_CERT}" -days 300 -extfile "${ACI_CONF}" -extensions v3_ca

echo "L'ACI et son certificat signé par l'ACR ont été créés."
