from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_mail import Mail, Message
import random
import requests

app = Flask(__name__)
CORS(app)

# Configuración de Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'aglmarquez2005@gmail.com'  # Cambia esto por tu correo
app.config['MAIL_PASSWORD'] = 'knmxjtcfjtsrktdp'  # Cambia esto por tu contraseña o App Password
app.config['MAIL_DEFAULT_SENDER'] = 'tu_correo@gmail.com'

mail = Mail(app)

# Almacenamiento temporal de códigos de verificación (en memoria)
verification_codes = {}

# Ruta para enviar el código de verificación
@app.route('/send-code', methods=['POST'])
def send_code():
    data = request.json
    email = data.get('email')
    phone = data.get('phone')

    if not email and not phone:
        return jsonify({'error': 'Correo o número de teléfono no proporcionado'}), 400

    # Generar un código de 6 dígitos
    verification_code = random.randint(100000, 999999)

    try:
        if email:
            # Enviar el código por correo
            verification_codes[email] = verification_code
            msg = Message('Código de Verificación', recipients=[email])
            msg.body = f'Tu código de verificación es: {verification_code}'
            mail.send(msg)
            print(f"Código enviado al correo {email}: {verification_code}")
            return jsonify({'message': 'Código enviado por correo correctamente'}), 200

        elif phone:
            # Enviar el código por WhatsApp
            verification_codes[phone] = verification_code
            url = "https://api.ultramsg.com/instance110919/messages/chat"
            payload = {
                "token": "wpt1sf4lepjdfu30",  # Reemplaza con tu token de UltraMsg
                "to": phone,
                "body": f"Tu código de verificación es: {verification_code}"
            }
            headers = {'content-type': 'application/x-www-form-urlencoded'}
            response = requests.post(url, data=payload, headers=headers)
            if response.status_code == 200:
                print(f"Código enviado al teléfono {phone}: {verification_code}")
                return jsonify({'message': 'Código enviado correctamente por WhatsApp'}), 200
            else:
                return jsonify({'error': 'Error al enviar el mensaje', 'details': response.text}), 500

    except Exception as e:
        return jsonify({'error': 'Error al enviar el código', 'details': str(e)}), 500

# Ruta para verificar el código ingresado
@app.route('/verify-code', methods=['POST'])
def verify_code():
    data = request.json
    email = data.get('email')
    phone = data.get('phone')
    code = data.get('code')

    if not (email or phone) or not code:
        return jsonify({'error': 'Correo, número de teléfono o código no proporcionado'}), 400

    # Identificar si se está verificando por correo o teléfono
    identifier = email if email else phone
    if identifier in verification_codes and verification_codes[identifier] == int(code):
        del verification_codes[identifier]  # Eliminar el código después de validarlo
        return jsonify({'message': 'Código verificado correctamente'}), 200
    else:
        return jsonify({'error': 'Código incorrecto o expirado'}), 400

if __name__ == '__main__':
    app.run(debug=True)