import os
import tensorflow as tf
import numpy as np

from ExpApp.Utils.datacore_constants import IMG_X
from ExpApp.datacore.EMG.EMGDataLoader import EMGDataLoader
from ExpApp.datacore.EMG.EMG_CNN import EMG_CNN
from ExpApp.datacore.EMG.EMGWindowSlicer import EMGWindowSlicer
from ExpApp.datacore.EMG.EMGDataLoader import EMGDataLoader


def train_tests():
    tests = [
        # end - start % 4 (CNN shrinkage) == 0
        # {"start": 140, "end": 300},
        # {"start": 0, "end": 200, "steps": 800},
        {"start": 0, "end": 200},
        # {"start": 100, "end": 360},
    ]
    for params in tests:
        _dir = "CNN_NN_" \
               + str(params["start"]) + "_" \
               + str(params["end"]) + "_" \
               + (str(params["bandpass"]) if "bandpass" in params else "" + "_") \
               + (str(params["learning_rate"]) if "learning_rate" in params else "" + "_") \
               + (str(params["steps"]) if "steps" in params else "" + "_") \
               + (str(params["momentum"]) if "momentum" in params else "")
        print(_dir)
        _dir = "CNN_EXPORT"

        input_fn = EMGDataLoader.load_data_for_cnn
        clf = EMG_CNN.train(model_dir=_dir, params=params, input_fn=input_fn)
        EMG_CNN.test(input_fn=input_fn, clf=clf, params=params)


def load_test(dir='CNNF_0_200____'):
    params = {
        "start": 0,
        "end": 200
    }
    input_fn = EMGDataLoader.load_data_for_cnn
    clf = EMG_CNN.load(model_dir="CNNF_0_200____", params=params)
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
    interpreter = tf.lite.Interpreter(model_path="models/converted_graph.tflite", )
    interpreter.allocate_tensors()

    # Get input and output tensors.
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    # Test model on random input data.
    input_shape = input_details[0]['shape']
    input_index = input_details[0]['index']
    interpreter.resize_tensor_input(input_index, input_shape)
    train, test = EMGDataLoader.load_data_for_cnn(params={"start": 0, "end": 200})

    input_data = np.array(np.random.random_sample(input_shape), dtype=np.float32)
    print(input_data.shape)
    for i in range(train.shape[0] // 20):
        input_data = train[i*20:i*20+20].reshape([20, 8, 200, 1])
        print(input_data.shape)
        interpreter.set_tensor(input_index, input_data)
        interpreter.invoke()

        output_data = interpreter.get_tensor(output_details[0]['index'])
        print(output_data.T)


if __name__ == '__main__':
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    # train_tests()
    # load_test()
    # load_test(dir='EMG_CNN_EXPORT/1544781666/')
    # export()
    # convert()
    test_tf_lite()
