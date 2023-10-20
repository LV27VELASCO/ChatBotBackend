import random
import json
import pickle
import numpy as np
import os  # Importa el módulo 'os' para manejar rutas
import nltk
from nltk.stem import WordNetLemmatizer
from flask import Flask, request, jsonify
from keras.models import load_model

app = Flask(__name__)
# from routes.users import guardar_en_historial

lemmatizer = WordNetLemmatizer()

# Importamos los archivos generados en el código anterior
intents = json.loads(open('intents.json', encoding='utf-8').read())
words = pickle.load(open('words.pkl', 'rb'))
classes = pickle.load(open('classes.pkl', 'rb'))
model = load_model('chatbot_model.h5')

# Pasamos las palabras de la oración a su forma raíz
def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word) for word in sentence_words]
    return sentence_words

# Convertimos la información a unos y ceros según si están presentes en los patrones
def bag_of_words(sentence):
    sentence_words = clean_up_sentence(sentence)
    bag = [0]*len(words)
    for w in sentence_words:
        for i, word in enumerate(words):
            if word == w:
                bag[i]=1
    return np.array(bag)

# Predecimos la categoría a la que pertenece la oración
def predict_class(sentence):
    bow = bag_of_words(sentence)
    res = model.predict(np.array([bow]))[0]
    max_index = np.where(res == np.max(res))[0][0]
    category = classes[max_index]
    return category

# Obtenemos una respuesta aleatoria
def get_response(tag, intents_json):
    list_of_intents = intents_json['intents']
    result = ""
    for i in list_of_intents:
        if i["tag"] == tag:
            result = random.choice(i['responses'])
            break
    return result

# Ruta para procesar solicitudes del chatbot
@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message = data.get('message', '')
    
    ints = predict_class(message)
    res = get_response(ints, intents)
    
    return jsonify({"response": res})

if __name__ == "__main__":
    app.run(port=5001, debug=True)


#Ejecutamos el chat en bucle
# while True:
#     message=input("")
#     ints = predict_class(message)
#     res = get_response(ints, intents)
#     print(res)
#     guardar_en_historial(message, res)
    

# # Función para procesar un mensaje del usuario y obtener una respuesta del chatbot
# def obtener_respuesta_del_chatbot(mensaje):
#     ints = predict_class(mensaje)
#     res = get_response(ints, intents)
#     return res