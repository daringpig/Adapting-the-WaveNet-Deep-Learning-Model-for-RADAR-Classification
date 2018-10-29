# -*- coding: utf-8 -*-
"""experiment_3.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1f3EirBVIpnCrl4vd8H4BW1gtEWnAxODP

# Experiment 3: Trained the network with 5 subjects at aspect angle 0 degree then tested on the 6th subject at aspect angles 0, 30, 45 and 60 degrees

*   Trained with 5 subjects at aspect angle 0 degrees
*   Tested on the 6th subject for 0, 30, 45 and 60 degrees
*   Modified from original paper to not validate on every test set for each epoch as Keras does not provide this functionality
*   **Possibly no walking?** **Wrong 0degrees test data**

## Notebook setup

Allow editing of modules using editor (auto reloading)
"""

# Needed to allow editing using PyCharm
# %load_ext autoreload
# %autoreload 2

"""Needed for compatibility when using both CoLab and Local Jupyter notebook. It sets the appropriate file path for the data and also installs local packages such as models and data_loading."""

import os
if os.getcwd() == '/content':
    from google.colab import drive
    drive.mount('/content/gdrive')
    BASE_PATH = '/content/gdrive/My Drive/Level-4-Project/'
    !cd gdrive/My\ Drive/Level-4-Project/ && pip install --editable .
    os.chdir('gdrive/My Drive/Level-4-Project/')
    
elif os.getcwd() == 'C:\\Users\\macka\\Google Drive\\Level-4-Project\\notebooks\\reproducing_original_experiments':
    BASE_PATH = "C:/Users/macka/Google Drive/Level-4-Project/"
    
else:
    BASE_PATH = "/export/home/2192793m/Level-4-Project/"
    
DATA_PATH = BASE_PATH + 'data/'
MODEL_PATH = BASE_PATH + 'models/original_experiments/experiment_3/'
FIGURE_PATH = BASE_PATH + 'reports/figures/original_experiments/experiment_3/'
REPORT_PATH = BASE_PATH + 'reports/original_experiments/experiment_3/'
    
from src.models.original_models import cnn_64_128
from src.data import load_data
from src.visualization import visualize

"""Import remaining packages"""

import numpy as np
import sys
from six.moves import cPickle
from keras.preprocessing.image import ImageDataGenerator
from keras.optimizers import SGD
from keras.utils import np_utils
import sys
from sklearn.metrics import classification_report,confusion_matrix
import csv
from keras.models import load_model

# Needed as originally code was for theano backend but now using tensor flow
from keras import backend as K
K.set_image_dim_ordering('th')

"""## Experiment Setup and Parameter Definition"""

data_folders = {'mixed_angle_A':{}, 'cifar_30deg':{}, 'cifar_45deg':{}, 'cifar_60deg':{}}
for key, value in data_folders.items():
    value["acc"] = None
    value["loss"] = None
    value["classification_report"] = None
    value["confusion_matrix"] = None
    
target_names = ['ArmFasterTowards', 'ArmSlowerTowards', 'CirclingArm', 'Clapping', 'PickingUp', 'Sitting']

load_model = False

batch_size = 100
nb_classes = 6
nb_epoch = 100
# nb_epoch = 1
nb_train_samples = 34260

# input image dimensions
img_rows, img_cols = 75, 75
# the CIFAR10 images are RGB

# the data, shuffled and split between train and test sets
(X_train, y_train), (X_test, y_test) = load_data.load_data((DATA_PATH + 'cifar_30deg'), nb_train_samples)
Y_train = np_utils.to_categorical(y_train, nb_classes)

"""## Training and Evaluating Models

### Train
"""

if load_model:
    model = load_model(MODEL_PATH + "cnn_64_128.h5")
else:
    model = cnn_64_128.make_model(img_rows, img_cols, nb_classes)
    # Train the model using SGD + momentum.
    sgd = SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
    model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])

    X_train = X_train.astype('float32')
    X_train /= 255

    history = model.fit(
        X_train,
        Y_train,
        batch_size=batch_size,
        epochs=nb_epoch,
        shuffle=True, 
        verbose=1)

"""### Evaluate for each Aspect Angle"""

for folder_name, value in data_folders.items():    
    X_test, y_test = load_data.load_batch(DATA_PATH + folder_name + '/test_batch')
    y_test = np.reshape(y_test, (len(y_test), 1))
    Y_test = np_utils.to_categorical(y_test, nb_classes)
    print(folder_name)
    evaluation = model.evaluate(X_test, Y_test, batch_size=batch_size, verbose=1)
    value["loss"] = evaluation[0]
    value["accuracy"] = evaluation[1]

    y_pred = model.predict_classes(X_test)
    value["classification_report"] = classification_report(
        np.argmax(Y_test,axis=1),
        y_pred,target_names=target_names)
    value["confusion_matrix"] = confusion_matrix(
        np.argmax(Y_test,axis=1), y_pred)

"""## Analysis and Saving of Results"""

save_graphs = True
save_model = True
save_report = True

"""### Plot and Save graphs"""

if not load_model:
    visualize.plot_train_acc(
        history, "Training Accuracy", save=save_graphs,
        path=FIGURE_PATH + "model_train_accuracy.svg")
    visualize.plot_train_loss(
        history, "Training Loss", save=save_graphs,
        path=FIGURE_PATH + "model_train_loss.svg")

visualize.plot_evaluation_bar(
    data_folders,
    ['0°','30°', '45°', '60°'],
    "Effect of Aspect Angle on Classification",
    'Aspect Angle',
    'Test Accuracy',
    save=save_graphs,
    path=FIGURE_PATH + "accuracy.svg")

visualize.plot_evaluation_bar(
    data_folders,
    ['0°','30°', '45°', '60°'],
    "Effect of Aspect Angle on Classification",
    'Aspect Angle',
    'Test Loss',
    metric="loss",
    save=save_graphs,
    path=FIGURE_PATH + "loss.svg")

"""### Save Model"""

if not load_model and save_model:
    model.save(MODEL_PATH + "cnn_64_128.h5")

"""### Save Classification Report and Confusion Matricies"""

if save_report:
    file = open(REPORT_PATH + 'Classification_and_Confusion.txt', 'w') 

    for folder_name, value in data_folders.items():    
        file.write("--------------------------------------------------\n") 
        file.write("Test set name: " + folder_name + "\n") 
        file.write("Accuracy: " + str(np.round(value["accuracy"], 2)) + "\n")
        file.write("Loss: " + str(np.round(value["loss"], 2)) + "\n")
        file.write("Classification Report:\n") 
        file.write(value['classification_report'])
        file.write("Confusion Matrix:\n") 
        file.write(np.array2string(value['confusion_matrix']) + "\n")

    file.close()
