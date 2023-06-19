#!/bin/bash


# Le script génère la clé privée de l'utilisateur (user_private_key.pem) et la CSR de l'utilisateur (user_csr.pem).

# Vérifiez si openssl est installé
if ! command -v openssl &> /dev/null; then
    echo "openssl n'est pas trouvé. Veuillez installer openssl et réessayer."
    exit 1
fi

# Générer la clé privée
openssl genpkey -algorithm EC -out user_private_key.pem -pkeyopt ec_paramgen_curve:P-521 -pkeyopt ec_param_enc:named_curve

# Créer un fichier de configuration pour la CSR
cat > csr_config.cnf << EOL
[ req ]
default_bits        = 521
distinguished_name  = req_distinguished_name
req_extensions      = req_ext
prompt              = no

[ req_distinguished_name ]
C  = FR
ST = Var
L  = Toulon
O  = ISEN
OU = ISEN
CN = project.mickey@outlook.com
emailAddress = project.mickey@outlook.com

[ req_ext ]
subjectAltName = @alt_names

[ alt_names ]
email.1 = project.mickey@outlook.com

[ usr_cert ]
basicConstraints=CA:FALSE
EOL

# Générer la CSR
openssl req -new -key user_private_key.pem -out user_csr.pem -config csr_config.cnf

echo "Clé privée : user_private_key.pem"
echo "CSR : user_csr.pem"
