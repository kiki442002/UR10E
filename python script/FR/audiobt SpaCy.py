import pyaudio
import speech_recognition as sr
import requests
import paho.mqtt.client as mqtt
import ssl
import time
import json
import spacy
import re

nlp = spacy.load("fr_core_news_sm")

# Fonction pour extraire les informations nécessaires à partir du texte
def extract_info(doc):
    order = None
    zone = None
    errors = []

    for token in doc:
        # Détection de l'ordre
        if token.lemma_.lower() in ["donner", "prendre"]:
            if token.lemma_.lower() == "donner":
                order = 1
            elif token.lemma_.lower() == "prendre":
                order = 2
        
        # Détection de la zone
        if token.text.isdigit():
            zone = int(token.text)
    
    # Gestion des erreurs
    if order is None:
        errors.append("Erreur : Impossible de déterminer l'ordre.")
    if zone is None:
        errors.append("Erreur : Impossible de déterminer la zone.")
    
    return order, zone, errors

# Fonction pour extraire les mouvements
def extract_movements(text):
    doc = nlp(text.lower())
    movement = {'order': 3, 'new_pos': [0, 0, 0, 0, 0, 0], 'target_point': 0, 'freedrive': 0, 'systeme_msg': ""}
    
    directions = {"avant": 1, "arrière": 1, "gauche": 0, "droite": 0, "haut": 2, "bas": 2}
    sign = {"avant": -1, "arrière": 1, "gauche": -1, "droite": 1, "haut": -1, "bas": 1}
    
    pattern = re.compile(r"(va\s+)?(haut|bas|gauche|droite|avant|arrière)\s+(à|de)\s*(\d+)", re.IGNORECASE)
    
    matches = pattern.findall(text.lower())
    
    for match in matches:
        _, direction, _, distance = match
        direction = direction.lower()
        distance = float(distance) / 100  # Convertir cm en mètres
        axis = directions[direction]
        movement['new_pos'][axis] = sign[direction] * distance

    if not matches:
        movement['order'] = -1
        movement['systeme_msg'] = "Erreur : Impossible de trouver une direction et une distance valides."
    
    return movement

# Fonction pour générer la commande JSON
def generate_command_json(order, zone, errors):
    command = {
        "order": order if errors == [] else -1,
        "new_pos": [0, 0, 0, 0, 0, 0],
        "target_point": zone if zone is not None else 0,
        "freedrive": 0,
        "systeme_msg": ", ".join(errors)
    }
    return json.dumps(command)

# Fonction pour générer la commande complète
def generate_command(text):
    doc = nlp(text.lower())
    command = {}

    # Identifier le type de commande
    if "prendre" in text.lower() or "donner" in text.lower():
        order, zone, errors = extract_info(doc)
        command = {
            "order": order if errors == [] else -1,
            "new_pos": [0, 0, 0, 0, 0, 0],
            "target_point": zone if zone is not None else 0,
            "freedrive": 0,
            "systeme_msg": ", ".join(errors)
        }
        if "libre" in text.lower():
            command["freedrive"] = 1
    elif "arrêter" in text.lower():
        command = {"order": 5, "new_pos": [0, 0, 0, 0, 0, 0], "target_point": 0, "freedrive": 0, "systeme_msg": ""}
    elif "maison" in text.lower():
        command = {"order": 6, "new_pos": [0, 0, 0, 0, 0, 0], "target_point": 0, "freedrive": 0, "systeme_msg": ""}
    elif any(direction in text.lower() for direction in ["avant", "arrière", "gauche", "droite", "haut", "bas"]):
        command = extract_movements(text.lower())
    else:
        if "libre" in text.lower():
            command = {"order": 4, "new_pos": [0, 0, 0, 0, 0, 0], "target_point": 0, "freedrive": 1, "systeme_msg": ""}
    
    return json.dumps(command)

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
    ch = input()  # Recevoir l'entrée sans imprimer de nouvelle ligne

    if ch.strip() == "":
        try:
            with micro as source:
                print("Parlez !")
                audio_data = r.listen(source, phrase_time_limit=5)
                print("Fin !")
                result = r.recognize_whisper(audio_data, model="base", language="fr")
                print(">", result)
        except sr.UnknownValueError:
            print("Désolé, je n’ai pas compris ce que vous avez dit.")
            result = False
        except sr.RequestError as e:
            print(f"Erreur de requête : {e}")

        if result:
            try:
                commandjson = generate_command(result)
                print(commandjson)

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

                    result = client.publish(topic, commandjson)
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
