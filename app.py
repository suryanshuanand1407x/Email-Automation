from flask import Flask, request, jsonify
from flask_mail import Mail, Message
from celery import Celery
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from datetime import timedelta
import smtplib

app = Flask(__name__)

# Setup config for Flask
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Use your email server
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your_email@gmail.com'
app.config['MAIL_PASSWORD'] = 'your_password'
app.config['SECRET_KEY'] = 'your_secret_key'

# Setup Mail and JWT
mail = Mail(app)
jwt = JWTManager(app)

# Celery Setup for Scheduling Emails
celery = Celery(app.name, broker='redis://localhost:6379/0')
celery.conf.update(app.config)

@app.route('/send_email', methods=['POST'])
@jwt_required()
def send_email():
    data = request.json
    recipient = data['recipient']
    subject = data['subject']
    body = data['body']
    
    # Create a message object
    msg = Message(subject=subject,
                  sender=app.config['MAIL_USERNAME'],
                  recipients=[recipient])
    msg.body = body

    # Send email
    try:
        mail.send(msg)
        return jsonify({"message": "Email sent successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@celery.task
def schedule_email(recipient, subject, body, send_time):
    # Delay the email sending using Celery
    from datetime import datetime
    while datetime.now() < send_time:
        time.sleep(1)  # Wait until send time
    send_email(recipient, subject, body)

if __name__ == '__main__':
    app.run(debug=True)