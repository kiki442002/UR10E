import pyaudio
import speech_recognition as sr
import requests
import paho.mqtt.client as mqtt
import ssl
import time
import json

# Configuration de la reconnaissance vocale
r = sr.Recognizer()
micro = sr.Microphone()

# Fonction de rappel pour gérer les messages entrants
def on_message(client, userdata, message):
    print(f"Message reçu sur le sujet {message.topic}: {message.payload.decode()}")

# Fonction de rappel pour vérifier la connexion
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connecté à MQTT Broker!")
    else:
        print(f"Échec de connexion, code de retour {rc}")

# Fonction de rappel pour vérifier la publication
def on_publish(client, userdata, mid):
    print("Message publié avec succès")

while True:
    ch = input()  # Receive input without printing a newline

    if ch.strip() == "":
        try:
            with micro as source:
                print("Parlez !")
                audio_data = r.listen(source, phrase_time_limit=5)
                print("Fin !")
                result = r.recognize_whisper(audio_data, model="base", language="en")
                print(">", result)
        except sr.UnknownValueError:
            print("Désolé, je n’ai pas compris ce que vous avez dit.")
            result = False
        except sr.RequestError as e:
            print(f"Erreur de requête : {e}")

        if result:
            url = "https://europe-west9-speech-robot-426314.cloudfunctions.net/speech_robot-speed-v2"
            body = {"text": result}

            try:
                response = requests.post(url, json=body)
                print(response.text)
                commandjson = json.loads(response.text)
                print(commandjson)
                commandjson = json.dumps(commandjson)

                client = mqtt.Client(client_id="myPy", transport='tcp', protocol=mqtt.MQTTv5)

                client.on_message = on_message
                client.on_connect = on_connect
                client.on_publish = on_publish

                broker = "192.168.4.1"
                port = 1883
                topic = "robot"
                client_id = f'python-mqtt-10'

                try:
                    client.connect(broker, port, 60)
                    client.loop_start()  # Démarrer la boucle pour gérer les messages entrants

                    result = client.publish(topic, response.text)
                    status = result[0]
                    if status == 0:
                        print(f"Message envoyé au topic {topic}")
                    else:
                        print(f"Échec d'envoi du message au topic {topic}")

                    time.sleep(1)  # Attendre pour s'assurer que le message est bien envoyé
                    client.loop_stop()
                    client.disconnect()
                except Exception as e:
                    print(f"Erreur de connexion MQTT : {e}")

            except requests.exceptions.RequestException as e:
                print(f"Erreur de requête API : {e}")

    print("ok")
