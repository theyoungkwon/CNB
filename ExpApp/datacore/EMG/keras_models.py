from __future__ import absolute_import, division, print_function, unicode_literals

import numpy as np
from sklearn import metrics
from sklearn.model_selection import train_test_split
from tensorflow_core.python.keras.layers.convolutional import Conv2D
from tensorflow_core.python.keras.layers.convolutional_recurrent import ConvLSTM2D
from tensorflow_core.python.keras.layers.core import Flatten, Dense
from tensorflow_core.python.keras.layers.normalization_v2 import BatchNormalization
from tensorflow_core.python.keras.layers.recurrent_v2 import LSTM
from tensorflow_core.python.keras.layers.wrappers import TimeDistributed
from tensorflow_core.python.keras.models import Sequential
from tensorflow_core.python.keras.optimizer_v2.adamax import Adamax
from tensorflow_core.python.keras.utils.np_utils import to_categorical

from ExpApp.Utils.datacore_constants import *
from ExpApp.datacore.DataLoader import DataLoader
import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'


def reshape_for_cnn(x):
    return x.reshape(x.shape + (1,))


def reshape_for_clstm(x):
    return x.reshape((len(x), 1) + x.shape[1:] + (1,))


def get_cnn(input_data, num_labels):
    model = Sequential()
    model.add(Conv2D(16, kernel_size=3, activation='relu', input_shape=input_data.shape))
    model.add(Conv2D(64, kernel_size=5, activation='relu'))
    model.add(Flatten())
    model.add(Dense(num_labels, activation='softmax'))
    opt = Adamax(learning_rate=LEARNING_RATE)
    model.compile(optimizer=opt, loss='categorical_crossentropy', metrics=['accuracy'])
    return model


def get_clstm(input_data, num_labels):
    model = Sequential()
    model.add(ConvLSTM2D(filters=16, kernel_size=(3, 3),
                         input_shape=input_data.shape,
                         padding='same', return_sequences=True))
    model.add(BatchNormalization())
    model.add(ConvLSTM2D(filters=64, kernel_size=(5, 5),
                         padding='same', return_sequences=False))
    model.add(BatchNormalization())
    model.add(Flatten())
    model.add(Dense(num_labels, activation='softmax'))
    opt = Adamax(learning_rate=LEARNING_RATE)
    model.compile(optimizer=opt, loss='categorical_crossentropy', metrics=['accuracy'])
    return model


def get_stacked_cnn_lstm(input_data, num_labels):
    model = Sequential()
    model.add(TimeDistributed(Conv2D(16, kernel_size=3, activation='relu', input_shape=input_data.shape)))
    model.add(TimeDistributed(Conv2D(64, kernel_size=5, activation='relu')))
    model.add(TimeDistributed(Flatten()))
    model.add(LSTM(units=2048))
    model.add(Dense(num_labels, activation='softmax'))
    opt = Adamax(learning_rate=LEARNING_RATE)

    model.compile(loss='categorical_crossentropy',
                  optimizer='sgd',
                  metrics=['accuracy'])
    return model


def test_model(model, x_train, x_test, y_train, y_test, epochs=5):
    model.fit(x_train, y_train, validation_data=(x_test, to_categorical(y_test)), batch_size=BATCH_SIZE, epochs=epochs,
              verbose=0)
    y_pred = model.predict(x_test * 1.)
    y_pred = [np.argmax(y, axis=None, out=None) for y in y_pred]
    accuracy = metrics.accuracy_score(y_test, y_pred)
    print(accuracy)
    return accuracy


def tests():
    subjects = [
        "s0",
        "s1",
        "s2",
        "s3",
        "s4",
        "s5",
        "s6",
        "s7",
        "s8",
        "s9"
    ]

    _set = SET7
    _end = 50
    _interval = 20

    for _subj in subjects:
        for _end in w_lengths:
            params = {"end": _end, "dir": _subj, "set": _set}
            x, y = DataLoader().load(params)

            print("CNN")
            x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, shuffle=True)
            y_train = to_categorical(y_train)
            x_train = reshape_for_cnn(x_train)
            x_test = reshape_for_cnn(x_test)
            cnn = get_cnn_adv(x_train[0], len(_set))
            model, accuracy = test_model(cnn, x_train, x_test, y_train, y_test)
            model.save(_subj + "_" + str(_end))


        print("CLSTM")
        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.1, shuffle=False, random_state=42)
        y_train = to_categorical(y_train)
        x_train = reshape_for_clstm(x_train)
        x_test = reshape_for_clstm(x_test)
        lstm = get_clstm(x_train[0], len(_set))
        test_model(lstm, x_train, x_test, y_train, y_test, epochs=3)

        print("S_CNN_LSTM")
        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.1, shuffle=False, random_state=42)
        y_train = to_categorical(y_train)
        x_train = reshape_for_clstm(x_train)
        x_test = reshape_for_clstm(x_test)
        s_cnn_lstm = get_stacked_cnn_lstm(x_train[0], len(_set))
        test_model(s_cnn_lstm, x_train, x_test, y_train, y_test)


if __name__ == '__main__':
    tests()
