from flask import Flask, request, redirect, render_template_string, url_for, send_from_directory
import os
import subprocess
import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import re

# Variables globales
absolute_path=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
user_email=""
user_cert_path=""
verification_code=0
output=""
zip_path=""

UPLOAD_FOLDER = f'{absolute_path}/code/webapp/static/uploads'
ALLOWED_EXTENSIONS = {'pem', 'csr'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Vérifier l'adresse e-mail de l'utilisateur (envoyer un code à usage unique)
def send_verification_code(email, code):
    print("__________________________________send_verification_code__________________________________")
    smtp_server = "smtp-relay.sendinblue.com"
    smtp_username = "project.sendinblue@outlook.com"
    smtp_password = "53Nh1AYWxqcd24Rz"
    sender_email = "project.sendinblue@outlook.com"

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = email
    message["Subject"] = "Code de validation de l'adresse mail"

    body = f"Voici votre code de vérification : {code}"
    message.attach(MIMEText(body, "plain"))

    with smtplib.SMTP_SSL(smtp_server, 465) as server:
        server.login(smtp_username, smtp_password)
        server.sendmail(sender_email, email, message.as_string())

# Vérifier le sujet du certificat
def check_csr_subject(csr_path,email):
    print("__________________________________check_csr_subject__________________________________")
    openssl_command = "/usr/bin/openssl req -in {} -noout -subject".format(csr_path)
    command = f"{openssl_command}"
    output = subprocess.check_output(command, shell=True)
    subject = output.decode().strip().split("emailAddress = ")[-1]
    if subject != email:
        return False
    return True

# Générer le certificat utilisateur
def generate_user_certificate(email,user_cert_uploaded):
    print("__________________________________generate_user_certificate__________________________________")
    global absolute_path
    user_cert_path = f"{absolute_path}/code/webapp/static/certs/{email}_cert.pem"
    user_cert_conf_path = f"{absolute_path}/code/webapp/static/certs/{email}_cert.conf"
    # Générer le certificat utilisateur signé par l'ACI
    subprocess.run(f"openssl x509 -req -in {user_cert_uploaded} -CA {absolute_path}/ACI/aci_cert.pem -CAkey {absolute_path}/ACI/aci_key.pem -CAcreateserial -out {user_cert_path} -days 30 -sha512 -extensions usr_cert", shell=True)

    return user_cert_path

# Gérer la requête de l'utilisateur
def process_user_request(email, verification_code, number, user_cert_uploaded):
    print("__________________________________process_user_request__________________________________")
    # Vérifier l'adresse e-mail de l'utilisateur
    received_code = number
    if received_code.strip() != verification_code:
        return

    # Générer le certificat utilisateur
    user_cert_path = generate_user_certificate(email,user_cert_uploaded)
    return user_cert_path

# Pages
def home_page():
    print("__________________________________home_page__________________________________")
    url_box = url_for('static', filename='box.css')
    url_button = url_for('static', filename='button.css')
    template = f'''
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" href="{url_box}">
        <link rel="stylesheet" href="{url_button}">
        <title>AE - Email</title>
    </head>
    <body>
        <div class="csr-box">
            <h2>Demande de signature de certificat</h2>
            <form action="/submit_csr" method="POST" enctype="multipart/form-data">
                <div class="user-box">
                    <input type="email" id="email" name="email" required>
                    <label>Email</label>
                </div>
                <div class="user-box">
                    <input type="file" id="csr" name="csr" accept=".csr,.pem" required>
                    <label></label>
                </div>
                <div><button method="POST" enctype="multipart/form-data" class="button-64" role="button" type="submit"><span class="text">Signer</span></button></div>
            </form>
            <form action="/revocation_home" method="GET" enctype="multipart/form-data">
                <div style="float:right"><button method="GET" enctype="multipart/form-data" class="button-85" role="button" type="submit">Révoquer</button></div>
            </form>
        </div>
    </body>
    </html>'''
    return template
    
def verify_code_page(user_email):
    print("__________________________________verify_code_page__________________________________")
    url_box = url_for('static', filename='box.css')
    url_button = url_for('static', filename='button.css')
    template = f'''
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" href="{url_box}">
        <link rel="stylesheet" href="{url_button}">
        <title>AE - Email</title>
    </head>
    <body>
        <div class="csr-box">
            <h2>Code de vérification</h2>
            <h3>envoyé à { user_email }</h3>
            <form action="/verify_code" method="POST" enctype="multipart/form-data">
                <div class="user-box">
                    <input type="text" id="number" name="number" required>
                    <label>Code</label>
                </div>
                <div><button method="POST" enctype="multipart/form-data" class="button-64" role="button" type="submit"><span class="text">Soumettre</span></button></div> 
            </form>
        </div>
    </body>
    </html>'''
    return template

def download_page(user_email, zip_path):
    print("__________________________________download_page__________________________________")
    url_box = url_for('static', filename='box.css')
    url_button = url_for('static', filename='button.css')


    template = f'''
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" href="{url_box}">
        <link rel="stylesheet" href="{url_button}">
        <title>AE - Email</title>
    </head>
    <body>
        <div class="csr-box">
            <h2>Vérification Réussis</h2>
            <h3>Télécharger votre certificat signé ci-dessous</h3>
            <a style="text-decoration:none" href="/certificates.zip" download>
                <div><button class="button-64" type="button"><span class="text">Télécharger Certificats</span></button></div>
            </a>
        </div>
    </body>
    </html>'''
    return template

def revocation_page():
    print("__________________________________revocation_page__________________________________")
    url_box = url_for('static', filename='box.css')
    url_button = url_for('static', filename='button.css')
    template = f'''
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" href="{url_box}">
        <link rel="stylesheet" href="{url_button}">
        <title>AE - Email</title>
    </head>
    <body>
        <div class="csr-box">
            <h2>Demande de révocation de certificat</h2>
            <form action="/revok_csr" method="POST" enctype="multipart/form-data">
                <div class="user-box">
                    <input type="email" id="email" name="email" required>
                    <label>Email</label>
                </div>
                <div class="user-box">
                    <input type="file" id="csr" name="csr" accept=".csr,.pem" required>
                    <label></label>
                </div>
                <div class="user-box">
                    <input type="text" id="raison" name="raison" required>
                    <label>Raison de la Révocation</label>
                </div>
                <div><button method="POST" enctype="multipart/form-data" class="button-64" role="button" type="submit"><span class="text">Révoquer</span></button></div>
            </form>
            <form action="/" method="GET" enctype="multipart/form-data">
                <div style="float:right"><button method="GET" enctype="multipart/form-data" class="button-85" role="button" type="submit">Signer</button></div>
            </form>
        </div>
    </body>
    </html>'''
    return template
 
def verify_revok_page(user_email):
    print("__________________________________verify_revok_page__________________________________")
    url_box = url_for('static', filename='box.css')
    url_button = url_for('static', filename='button.css')
    template = f'''
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" href="{url_box}">
        <link rel="stylesheet" href="{url_button}">
        <title>AE - Email</title>
    </head>
    <body>
        <div class="csr-box">
            <h2>Code de vérification</h2>
            <h3>envoyé à { user_email }</h3>
            <form action="/verify_revok" method="POST" enctype="multipart/form-data">
                <div class="user-box">
                    <input type="text" id="number" name="number" required>
                    <label>Code</label>
                </div>
                <div><button method="POST" enctype="multipart/form-data" class="button-64" role="button" type="submit"><span class="text">Soumettre</span></button></div> 
            </form>
        </div>
    </body>
    </html>'''
    return template

def end_revok_page():
    print("__________________________________end_revok_page__________________________________")
    url_box = url_for('static', filename='box.css')
    url_button = url_for('static', filename='button.css')
    template = f'''
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" href="{url_box}">
        <link rel="stylesheet" href="{url_button}">
        <title>AE - Email</title>
    </head>
    <body>
        <div class="csr-box">
            <h2>Révocation du certificat Réussis</h2>
            <form action="/" method="GET" enctype="multipart/form-data">
                <div style="float:right"><button method="GET" enctype="multipart/form-data" class="button-85" role="button" type="submit">Accueil</button></div>
            </form>
        </div>
    </body>
    </html>'''
    return template

# Routes Flask
@app.route('/certificates.zip')
def download_certificates():
    print("__________________________________download_certificates__________________________________")
    global zip_path
    global user_email
    return send_from_directory(f'{zip_path}', f'{user_email}_cert.zip', as_attachment=True)
@app.route('/')
def index():
    print("__________________________________index__________________________________")
    return render_template_string(home_page())

@app.route('/submit_csr', methods=['POST'])
def submit_csr():
    print("__________________________________submit_csr__________________________________")
    global user_email
    global user_cert_path
    global verification_code
    global absolute_path
    user_email = request.form.get('email')
    user_cert_path = request.files['csr']
    user_cert_path.save(os.path.join(app.config['UPLOAD_FOLDER'], user_cert_path.filename))
    user_cert_path = f"{absolute_path}/code/webapp/static/uploads/"+user_cert_path.filename

    #regex_mail = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
    regex_mail = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

    if re.fullmatch(regex_mail, user_email):
        # Vérifier si le sujet est bon 
        if check_csr_subject(user_cert_path,user_email):
        
            # Générer un code de vérification et l'envoyer à l'adresse e-mail de l'utilisateur
            verification_code = str(random.randint(10000000, 99999999))
            send_verification_code(user_email, verification_code)

            return verify_code_page(user_email)
        else:
            return "Erreur : le sujet du CSR ne correspond pas à l'adresse e-mail soumise.", 400

    else:
        return "Erreur : veuillez soumettre le formulaire avec votre adresse e-mail.", 400

@app.route('/verify_code', methods=['POST'])
def verify_code():
    print("__________________________________verify_code__________________________________")
    global output
    global user_email
    global user_cert_path
    global absolute_path
    global zip_path
    number = request.form.get('number')
    # Traiter la demande de l'utilisateur
    output = process_user_request(user_email, verification_code, number, user_cert_path)
    if output:
        user_cert_path = output
        
        # Création du zip contenant les certificats

        zip_path = subprocess.run(f"zip -j {absolute_path}/code/webapp/static/zip/{user_email}_cert.zip {user_cert_path} {absolute_path}/ACI/aci_cert.pem {absolute_path}/ACR/acr_cert.pem", shell=True)
        zip_path = f"{absolute_path}/code/webapp/static/zip"
        return download_page(user_email, zip_path)
    else:
        return "Erreur: Le code de vérification n'est pas bon."

@app.route('/revocation_home')
def revocation_home():
    print("__________________________________revocation_home__________________________________")
    return revocation_page()

@app.route('/revok_csr', methods=['POST'])
def revok_csr():
    print("__________________________________revok_csr__________________________________")
    global user_email
    global user_cert_path
    global verification_code
    user_email = request.form.get('email')
    revok_reason = request.form.get('raison')
    print(revok_reason)
    regex_mail = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')

    if re.fullmatch(regex_mail, user_email):
        # Générer un code de vérification et l'envoyer à l'adresse e-mail de l'utilisateur
        verification_code = str(random.randint(10000000, 99999999))
        send_verification_code(user_email, verification_code)

        return verify_revok_page(user_email)

    else:
        return "Erreur : veuillez soumettre le formulaire avec votre adresse e-mail.", 400

@app.route('/verify_revok', methods=['POST'])
def verify_revok():
    print("__________________________________verify_revok__________________________________")
    global output
    global user_email
    number = request.form.get('number')
    # Traiter la demande de l'utilisateur
    output = process_user_request(user_email, verification_code, number)

    if number.strip() == verification_code:
        # Révoquer le certificat de l'utilisateur
        return end_revok_page()
    else:
        return "Erreur: Le code de vérification n'est pas bon."

if __name__ == '__main__':
    app.run()
