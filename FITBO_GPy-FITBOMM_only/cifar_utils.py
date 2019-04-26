#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 27 15:36:29 2019

@author: jian
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 27 15:06:52 2019

@author: jian
"""

'''
#Train a simple deep CNN on the CIFAR10 small images dataset.
It gets to 75% validation accuracy in 25 epochs, and 79% after 50 epochs.
(it's still underfitting at that point, though).
'''

import keras
from keras.datasets import cifar10
from keras.preprocessing.image import ImageDataGenerator
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, Flatten
from keras.layers import Conv2D, MaxPooling2D
import os
import numpy as np
from tensorflow import set_random_seed

num_classes = 10
epochs = 1 #20

# The data, split between train and test sets:
(x_train, y_train), (x_test, y_test) = cifar10.load_data()
# Convert class vectors to binary class matrices.
y_train = keras.utils.to_categorical(y_train, num_classes)
y_test = keras.utils.to_categorical(y_test, num_classes)
x_train = x_train.astype('float32')
x_test = x_test.astype('float32')
x_train /= 255
x_test /= 255

params_simple = {"batch_size": 32,
          "l1_dropout": 0.25,
          "l2_dropout": 0.25,
          "l3_dropout": 0.5,
          "rms_l_rate": 0.0001,
          "fc_units": 512,
          }

params_complex = {"batch_size": 32,
          "l1_dropout": 0.25,
          "l2_dropout": 0.25,
          "l3_dropout": 0.5,
          "rms_l_rate": 0.0001,
          "l1_conv_filter": 32,
          "l2_conv_filter": 32,
          "l3_conv_filter": 64,
          "l4_conv_filter": 64,
          "dense_units": 512,
          "activation1": "relu",
          "activation2": "relu",
          "activation3": "relu",
          "activation4": "relu",
          }

def cifar_cnn_gpyopt(x):

    # Unwrapping X into parameters
    x = np.ravel(x)

    batch_size = int(x[0])
    fc_units = int(x[1])
    l1_dropout = x[2]
    l2_dropout = x[3]
    l3_dropout = x[4]
    rms_l_rate = x[5]

    model = Sequential()
    model.add(Conv2D(32, (3, 3), padding='same', # l1_conv_filter
                     input_shape=x_train.shape[1:]))
    model.add(Activation('relu'))
    model.add(Conv2D(32, (3, 3)))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(l1_dropout))

    model.add(Conv2D(64, (3, 3), padding='same'))
    model.add(Conv2D(64, (3, 3)))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(l2_dropout))

    model.add(Flatten())
    model.add(Dense(fc_units))
    model.add(Activation('relu'))
    model.add(Dropout(l3_dropout))
    model.add(Dense(num_classes))
    model.add(Activation('softmax'))

    # initiate RMSprop optimizer
    opt = keras.optimizers.rmsprop(lr=rms_l_rate, decay=1e-6)

    # Let's train the model using RMSprop
    model.compile(loss='categorical_crossentropy',
                  optimizer=opt,
                  metrics=['accuracy'])

    # Fit the model
    model.fit(x_train, y_train,
              batch_size=batch_size,
              epochs=epochs,
              validation_data=(x_test, y_test),
              shuffle=True)

    scores = model.evaluate(x_test, y_test, verbose=0)
    test_accuracy = scores[1]

    return -test_accuracy # negative because FITBO minimises

def cifar_cnn_fitbo(X):
    # same as gpyopt_objective, except X is size (num_iter, input_dim)
    y = np.zeros((X.shape[0], 1))

    for i in range(X.shape[0]):
        y[i] = cifar_cnn_gpyopt(X[i])

    return y
