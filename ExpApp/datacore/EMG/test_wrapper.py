import datetime
import os
import time
from random import randint

import tensorflow as tf
import numpy as np

from ExpApp.Utils.datacore_constants import IMG_X, SET1, SET2, SET3, SET4, SET5
from ExpApp.datacore.EMG.EMG_CNN import EMG_CNN
from ExpApp.datacore.EMG.EMGDataLoader import EMGDataLoader


def train_tests():
    subjects = [
        # "s1",
        # "s2",
        # "s3",
        # "s4",
        # "s5",
        # "s6",
        "s7",
    ]
    sets = [
        SET1,
        SET2,
        SET3,
        SET4,
        SET5,
    ]
    # sample_test = {"start": 0, "end": 200, "dir": "s1/", "set": SET5}

    tests = [
        # end - start % 4 (CNN shrinkage) == 0
        {"start": 0, "end": 200, "dir": "s1", "set": SET1},
        {"start": 0, "end": 200, "dir": "s1", "set": SET2},
        {"start": 0, "end": 200, "dir": "s1", "set": SET3},
        {"start": 0, "end": 200, "dir": "s1", "set": SET4},
        {"start": 0, "end": 200, "dir": "s1", "set": SET5},

        {"start": 0, "end": 200, "dir": "s2", "set": SET1},
        {"start": 0, "end": 200, "dir": "s2", "set": SET2},
        {"start": 0, "end": 200, "dir": "s2", "set": SET3},
        {"start": 0, "end": 200, "dir": "s2", "set": SET4},
        {"start": 0, "end": 200, "dir": "s2", "set": SET5},

        {"start": 0, "end": 200, "dir": "s3", "set": SET1},
        {"start": 0, "end": 200, "dir": "s3", "set": SET2},
        {"start": 0, "end": 200, "dir": "s3", "set": SET3},
        {"start": 0, "end": 200, "dir": "s3", "set": SET4},
        {"start": 0, "end": 200, "dir": "s3", "set": SET5},

        {"start": 0, "end": 200, "dir": "s4", "set": SET1},
        {"start": 0, "end": 200, "dir": "s4", "set": SET2},
        {"start": 0, "end": 200, "dir": "s4", "set": SET3},
        {"start": 0, "end": 200, "dir": "s4", "set": SET4},
        {"start": 0, "end": 200, "dir": "s4", "set": SET5},

        {"start": 0, "end": 200, "dir": "s5", "set": SET1},
        {"start": 0, "end": 200, "dir": "s5", "set": SET2},
        {"start": 0, "end": 200, "dir": "s5", "set": SET3},
        {"start": 0, "end": 200, "dir": "s5", "set": SET4},
        {"start": 0, "end": 200, "dir": "s5", "set": SET5},

        {"start": 0, "end": 200, "dir": "s6", "set": SET1},
        {"start": 0, "end": 200, "dir": "s6", "set": SET2},
        {"start": 0, "end": 200, "dir": "s6", "set": SET3},
        {"start": 0, "end": 200, "dir": "s6", "set": SET4},
        {"start": 0, "end": 200, "dir": "s6", "set": SET5},

        {"start": 0, "end": 200, "dir": "s7", "set": SET1},
        {"start": 0, "end": 200, "dir": "s7", "set": SET2},
        {"start": 0, "end": 200, "dir": "s7", "set": SET3},
        {"start": 0, "end": 200, "dir": "s7", "set": SET4},
        {"start": 0, "end": 200, "dir": "s7", "set": SET5},
    ]

    # for subject in subjects:
    #     for _set in sets:
    #         test = sample_test
    #         test["dir"] = subject
    #         test["set"] = _set
    #         tests.append(test)

    i = 0
    for params in tests:
        i += 1
        _dir = params["dir"] + "_" + str(len(params["set"])) + "_" +  str(randint(0, 10000)) + "_" \
               + str(params["start"]) + "_" \
               + str(params["end"]) + "_" \
               + (str(params["bandpass"]) if "bandpass" in params else "" + "_") \
               + (str(params["learning_rate"]) if "learning_rate" in params else "" + "_") \
               + (str(params["steps"]) if "steps" in params else "" + "_") \
               + (str(params["momentum"]) if "momentum" in params else "")
        print(_dir)
        # _dir = "CNN_EXPORT"

        start_time = int(round(time.time() * 1000))
        input_fn = EMGDataLoader.load_data_for_cnn
        # input_fn = ninaЛ
        clf = EMG_CNN.train(model_dir=_dir, params=params, input_fn=input_fn)
        # clf = EMG_CNN.load(model_dir=_dir, params=params    )
        EMG_CNN.test(input_fn=input_fn, clf=clf, params=params)
        end_time = int(round(time.time() * 1000))
        print(end_time - start_time)


def load_test():
    params = {
        "start": 0,
        "end": 180
    }
    input_fn = EMGDataLoader.load_data_for_cnn
    clf = EMG_CNN.load(model_dir="CNN_CHANNELS_2_0_180____", params=params)
    EMG_CNN.test(input_fn=input_fn, clf=clf, params=params)


def serving_input_receiver_fn():
    inputs = {
        "x": tf.placeholder(tf.float32, [None, IMG_X, 200, 1]),
    }
    return tf.estimator.export.ServingInputReceiver(inputs, inputs)


def export():
    params = {
        "start": 0,
        "end": 200
    }
    export_dir = 'models/EMG_CNN_EXPORT/'
    estimator = EMG_CNN.load(model_dir="CNN_NX_0_200___800", params=params)
    estimator.export_savedmodel(export_dir, serving_input_receiver_fn=serving_input_receiver_fn)


def convert():
    export_dir = 'models/EMG_CNN_EXPORT/1544781666'
    converter = tf.lite.TFLiteConverter.from_saved_model(export_dir)
    tflite_model = converter.convert()
    open("converted_model.tflite", "wb").write(tflite_model)


def test_tf_lite():
    # Load TFLite model and allocate tensors.
    interpreter = tf.lite.Interpreter(model_path="models/4PCA_graph.tflite", )
    interpreter.allocate_tensors()

    # Get input and output tensors.
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    # Test model on random input data.
    input_shape = input_details[0]['shape']
    input_index = input_details[0]['index']
    batch_size = 20
    WINDOW_END = 200
    shape = [batch_size, IMG_X, WINDOW_END, 1]
    interpreter.resize_tensor_input(input_index, shape)
    train, test = EMGDataLoader.load_data_for_cnn(params={"start": 0, "end": WINDOW_END})

    for i in range(train.shape[0] // batch_size):
        input_data = train[i * batch_size:i * batch_size + batch_size].reshape(shape)
        start = int(round(time.time() * 1000))
        interpreter.set_tensor(input_index, input_data)
        interpreter.invoke()
        output_data = interpreter.get_tensor(output_details[0]['index'])
        end = int(round(time.time() * 1000))
        print(str((end - start) / batch_size) + ":" + str(output_data.T))


if __name__ == '__main__':
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    tf.logging.set_verbosity(tf.logging.ERROR)
    train_tests()
    # load_test()
    # load_test(dir='EMG_CNN_EXPORT/1544781666/')
    # export()
    # convert()
    # test_tf_lite()
