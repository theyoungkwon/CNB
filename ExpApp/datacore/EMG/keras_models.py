from __future__ import absolute_import, division, print_function, unicode_literals

import os

from tensorflow_core.lite.python.interpreter import Interpreter
from tensorflow_core.lite.python.lite import TFLiteConverter

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
import tensorflow as tf
import matplotlib.pyplot as plt
import numpy as np
from sklearn import metrics
from sklearn.model_selection import train_test_split, KFold
from tensorflow_core.python.keras.callbacks import EarlyStopping
from tensorflow_core.python.keras.layers.convolutional import Conv2D
from tensorflow_core.python.keras.layers.convolutional_recurrent import ConvLSTM2D
from tensorflow_core.python.keras.layers.core import Flatten, Dense, Dropout
from tensorflow_core.python.keras.layers.normalization_v2 import BatchNormalization
from tensorflow_core.python.keras.layers.pooling import MaxPooling2D
from tensorflow_core.python.keras.layers.recurrent_v2 import LSTM
from tensorflow_core.python.keras.layers.wrappers import TimeDistributed
from tensorflow_core.python.keras.models import Sequential
from tensorflow_core.python.keras.optimizer_v2.adam import Adam
from tensorflow_core.python.keras.optimizer_v2.adamax import Adamax
from tensorflow_core.python.keras.utils.np_utils import to_categorical
from tensorflow_core.python.keras import backend

from ExpApp.Utils.KeyfileMerger import KeyfileMerger
from ExpApp.Utils.confusion_matrix_printer import plot_confusion_matrix
from ExpApp.Utils.datacore_constants import *
from ExpApp.datacore.DataLoader import DataLoader
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay


def reshape_for_cnn(x):
    return x.reshape(x.shape + (1,))


def reshape_for_clstm(x):
    return x.reshape((len(x), 1) + x.shape[1:] + (1,))


def get_cnn(input_data, num_labels):
    model = Sequential()
    model.add(Conv2D(16, kernel_size=2, activation='relu', input_shape=input_data.shape))
    model.add(Conv2D(64, kernel_size=3, activation='relu'))
    model.add(Conv2D(128, kernel_size=3, activation='relu'))
    model.add(Flatten())
    model.add(Dense(num_labels, activation='softmax'))
    opt = Adamax(learning_rate=LEARNING_RATE)
    model.compile(optimizer=opt, loss='categorical_crossentropy', metrics=['accuracy'])
    return model


def get_cnn_adv(input_data, num_labels):
    model = Sequential()
    div = 4
    model.add(Conv2D(64, kernel_size=(input_data.shape[0] // div, 1), activation='relu', input_shape=input_data.shape))
    model.add(Conv2D(128, kernel_size=(div, 8), activation='relu'))
    model.add(Flatten())
    model.add(Dense(500, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(num_labels, activation='softmax'))
    opt = Adamax(learning_rate=KeyConstants.ELR)
    model.compile(loss='categorical_crossentropy', opt=opt, metrics=['accuracy'])
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


def get_pen_cnn(input_data, num_labels):
    model = Sequential()
    model.add(Conv2D(64, kernel_size=(3, 3), activation='relu', input_shape=input_data.shape))
    model.add(MaxPooling2D(pool_size=2, strides=2))
    model.add(Conv2D(128, kernel_size=(3, 3), activation='relu'))
    model.add(Flatten())
    model.add(Dense(500, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(num_labels, activation='softmax'))

    opt = Adam(learning_rate=.0003)

    model.compile(loss='categorical_crossentropy', opt=opt, metrics=['accuracy'])
    return model


def test_model(model, x_train, x_test, y_train, y_test, epochs=KERAS_EPOCHS):
    callbacks = []
    model.fit(x_train, y_train, validation_data=(x_test, to_categorical(y_test)), batch_size=KERAS_BATCH_SIZE,
              epochs=epochs, callbacks=callbacks,
              verbose=1)
    y_pred = model.predict(x_test * 1.)
    y_pred = [np.argmax(y, axis=None, out=None) for y in y_pred]
    accuracy = metrics.accuracy_score(y_test, y_pred)
    plot_confusion_matrix(y_true=np.asarray(y_test).astype(int),
                          y_pred=np.asarray(y_pred).astype(int),
                          title=str(accuracy), normalize=True,
                          classes=[str(i + 1) for i in range(len(y_train[0]))])
    return model, accuracy


def test_model_new(model, x_train, x_test, y_train, y_test, epochs=KERAS_EPOCHS):
    model.fit(x_train, y_train, validation_data=(x_test, to_categorical(y_test)), batch_size=KERAS_BATCH_SIZE,
              epochs=epochs,
              verbose=1)
    y_pred = model.predict(np.ndarray.astype(x_test, 'float32'))
    y_pred = [np.argmax(y, axis=None, out=None) for y in y_pred]
    accuracy = metrics.accuracy_score(y_test, y_pred)
    plot_confusion_matrix(y_true=np.asarray(y_test).astype(int),
                          y_pred=np.asarray(y_pred).astype(int),
                          title=str(accuracy), normalize=True,
                          classes=[str(i + 1) for i in range(len(y_train[0]))])
    return model, accuracy


def train_models_main():
    subjects = [PARTICIPANT_LIST[0]]

    _set = BUZZ_SET

    w_lengths = [WINDOW_LENGTHS[0]]

    total_accuracy = 0.0

    count = 0

    for _subj in subjects:
        for _end in w_lengths:
            params = {"end": _end, "dir": _subj, "set": _set}
            print(f"CNN {_subj}, {_end}")

            x, y = DataLoader().load(params)
            x = scale_input(x)
            x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, shuffle=True)
            y_train = to_categorical(y_train)
            x_train = reshape_for_cnn(x_train)
            x_test = reshape_for_cnn(x_test)

            cnn = get_cnn_adv(x_train[0], len(_set))
            model, accuracy, cm = test_model(cnn, x_train, x_test, y_train, y_test)
            model_name = _subj + "_" + str(_end)
            model.save(model_name)

            count += 1
            total_accuracy += accuracy

    print("Average accuracy is " + str(total_accuracy / count))

    return model_name


def key_test():
    merger = KeyfileMerger()
    merger.load_files()
    merger.merge()
    merger.analyse()
    x, y = merger.cut_trials()
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.1, shuffle=True, random_state=42)
    y_train = to_categorical(y_train)
    x_train = reshape_for_cnn(x_train)
    x_test = reshape_for_cnn(x_test)
    cnn = get_cnn(x_train[0], len(y_train[0]))
    model, accuracy, cm = test_model(cnn, x_train, x_test, y_train, y_test)
    model.save(KeyConstants.MODEL_PATH)


def kfold(k=5):
    subjects = PARTICIPANT_LIST
    w_lengths = [100, 50, 25, 5]

    for _end in w_lengths:
        print(_end)
        for _subj in subjects:
            # if True:  # total
            # if _subj.find("pen") >= 0:
            # if _subj.find("umbr") >= 0:
            if _subj.find("pen") < 0 and _subj.find("umbr") < 0:  # fh
                print(f"subj: {_subj} len: {_end}")
                params = {"end": _end, "dir": _subj, "set": INPUT_SET}
                x, y = DataLoader().load(params)
                x = scale_input(x)

                kf = KFold(n_splits=k, shuffle=True, random_state=293)

                for train_index, test_index in kf.split(x):
                    x_train, x_test = x[train_index], x[test_index]
                    y_train, y_test = y[train_index], y[test_index]

                    y_train = to_categorical(y_train)
                    x_train = reshape_for_cnn(x_train)
                    x_test = reshape_for_cnn(x_test)

                    cnn = get_cnn_adv(x_train[0], len(INPUT_SET))
                    model, accuracy, cm = test_model(cnn, x_train, x_test, y_train, y_test)
                    print(accuracy)

                    backend.clear_session()

    pass


def get_gcm():
    subjects = PARTICIPANT_LIST

    _set = INPUT_SET

    _end = 50

    cum_cm = np.zeros((len(INPUT_SET), len(INPUT_SET)))

    print(f'cm for length {_end}')

    count = 0

    for _subj in subjects:
        # if _subj.find("pen") >= 0:
        # if _subj.find("umbr") >= 0:
        if _subj.find("pen") < 0 and _subj.find("umbr") < 0:  # fh
            count += 1
            params = {"end": _end, "dir": _subj, "set": _set}
            x, y = DataLoader().load(params)
            x = scale_input(x)
            x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, shuffle=True)
            y_train = to_categorical(y_train)
            x_train = reshape_for_cnn(x_train)
            x_test = reshape_for_cnn(x_test)
            cnn = get_cnn_adv(x_train[0], len(_set))
            model, accuracy, cm = test_model(cnn, x_train, x_test, y_train, y_test)
            cum_cm += cm
            print(accuracy)

    ax = plt.axes()
    ax.ylabel = "Target"
    mx = cum_cm
    mx = mx / count  # normalize dat
    disp = ConfusionMatrixDisplay(confusion_matrix=mx, display_labels=["suggestion", "top", "mid", "bottom", "rest"])
    disp.plot(include_values=True, ax=ax, cmap='Blues')
    plt.show()

def get_tflite_from_existing_model(model_name):
    converter = TFLiteConverter.from_keras_model_file(model_name)
    tflite_model = converter.convert()
    open(model_name + '.tflite', "wb").write(tflite_model)


def get_tflite():
    _set = INPUT_SET
    _subj = "kirillpen"

    w_lengths = [100, 50, 25, 10]

    for _end in w_lengths:
        params = {"end": _end, "dir": _subj, "set": _set}
        x, y = DataLoader().load(params)
        x = scale_input(x)
        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, shuffle=True)
        y_train = to_categorical(y_train)
        x_train = reshape_for_cnn(x_train)
        x_test = reshape_for_cnn(x_test)
        cnn = get_cnn_adv(x_train[0], len(_set))
        model, accuracy, cm = test_model(cnn, x_train, x_test, y_train, y_test)
        model_name = f"{_subj}_{_end}"
        model.save(model_name)
        converter = TFLiteConverter.from_keras_model_file(model_name)
        tflite_model = converter.convert()
        open(model_name + '.tflite', "wb").write(tflite_model)


def validate_tflite(model_name):
    interpreter = Interpreter(model_path=model_name)
    interpreter.allocate_tensors()
    # Get input and output tensors
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    # Test model on random input data
    input_shape = input_details[0]['shape']
    input_data = np.array(np.random.random_sample(input_shape), dtype=np.float32)
    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()
    output_data = interpreter.get_tensor(output_details[0]['index'])
    print(output_data)  # softmax layer


if __name__ == '__main__':
    # model_name = f"{PARTICIPANT_LIST[0]}_{WINDOW_LENGTHS[0]}"
    model_name = train_models_main()
    get_tflite_from_existing_model(model_name)
    validate_tflite(model_name + ".tflite")
