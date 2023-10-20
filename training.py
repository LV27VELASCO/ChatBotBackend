import random
import json
import pickle
import numpy as np
import os  # Importa el módulo 'os' para manejar rutas

import nltk
from nltk.stem import WordNetLemmatizer

import tensorflow as tf
from keras.models import Sequential
from keras.layers import Dense, Activation, Dropout

lemmatizer = WordNetLemmatizer()

# Obtiene la ruta completa al archivo intents.json en la carpeta models
current_folder = os.path.dirname(os.path.abspath(__file__))
intents_path = os.path.join(current_folder, 'intents.json')

intents = json.loads(open(intents_path, encoding='utf-8').read())  # Usa la ruta completa

nltk.download('punkt')
nltk.download('wordnet')
nltk.download('omw-1.4')

words = []
classes = []
documents = []
ignore_letters = ['?', '!', '¿', '.', ',']

# Clasifica los patrones y las categorías
for intent in intents['intents']:
    for pattern in intent['patterns']:
        word_list = nltk.word_tokenize(pattern)
        words.extend(word_list)
        documents.append((word_list, intent["tag"]))
        if intent["tag"] not in classes:
            classes.append(intent["tag"])

words = [lemmatizer.lemmatize(word) for word in words if word not in ignore_letters]
words = sorted(set(words))

pickle.dump(words, open('words.pkl', 'wb'))
pickle.dump(classes, open('classes.pkl', 'wb'))

# Pasa la información a unos y ceros según las palabras presentes en cada categoría para hacer el entrenamiento
training = []
output_empty = [0] * len(classes)
max_length = max(len(item[0]) for item in documents)  # Mover este cálculo aquí

for document in documents:
    bag = []
    word_patterns = document[0]
    word_patterns = [lemmatizer.lemmatize(word.lower()) for word in word_patterns]
    for word in words:
        bag.append(1) if word in word_patterns else bag.append(0)
    output_row = list(output_empty)
    output_row[classes.index(document[1])] = 1
    training.append([bag, output_row])

# Asegurarse de que todas las sub-listas tengan la misma longitud
max_length = max(len(item[0]) for item in training)
training_data = []

for item in training:
    input_data = item[0]
    output_data = item[1]
    
    # Rellenar las sublistas para que tengan la misma longitud
    while len(input_data) < max_length:
        input_data.append(0)
    
    # Asegurarse de que output_data tenga la misma longitud que classes
    while len(output_data) < len(classes):
        output_data.append(0)
    
    training_data.append([input_data, output_data])

# Convertir la lista de sublistas en un arreglo NumPy
training_data = np.array(training_data, dtype=object)  # Utilizar dtype=object para permitir listas en el arreglo
print(training_data)

# #Reparte los datos para pasarlos a la red
train_x = list(training_data[:,0])
train_y = list(training_data[:,1])

# Crear un programa de decaimiento de la tasa de aprendizaje
learning_rate_schedule = tf.keras.optimizers.schedules.ExponentialDecay(
    initial_learning_rate=0.001,
    decay_steps=10000,
    decay_rate=0.9
)

# Crear el optimizador con el programa de decaimiento de la tasa de aprendizaje
sgd = tf.keras.optimizers.SGD(learning_rate=learning_rate_schedule, momentum=0.9, nesterov=True)

# Crear el modelo y compilarlo con el nuevo optimizador
model = Sequential()
model.add(Dense(128, input_shape=(len(train_x[0]),), activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(64, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(len(train_y[0]), activation='softmax'))

model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])

# Entrenar el modelo y guardarlo
train_process = model.fit(np.array(train_x), np.array(train_y), epochs=100, batch_size=5, verbose=1)
model.save("chatbot_model.h5", train_process)