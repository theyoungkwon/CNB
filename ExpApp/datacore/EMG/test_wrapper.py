import os

from EMG.EMGConnector import EMGConnector
from ExpApp.Utils.datacore_constants import TC_B, TC_E, LEARNING_RATE
from ExpApp.datacore.EMG.EMG_CNN import EMG_CNN
from ExpApp.datacore.EMG.EMGWindowSlicer import EMGWindowSlicer
from ExpApp.datacore.EMG.EMGDataLoader import EMGDataLoader


def train_tests():
    tests = [
        # end - start % 4 (CNN shrinkage) == 0
        # {"start": 140, "end": 300},
        {"start": 0, "end": 200, "steps": 800},
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

        input_fn = EMGDataLoader.load_data_for_cnn
        clf = EMG_CNN.train(model_dir=_dir, params=params, input_fn=input_fn)
        EMG_CNN.test(input_fn=input_fn, clf=clf, params=params)


def load_test():
    params = {
        "start": 0,
        "end": 200
    }
    input_fn = EMGDataLoader.load_data_for_cnn
    clf = EMG_CNN.load(model_dir="CNNF_0_200____", params=params)
    EMG_CNN.test(input_fn=input_fn, clf=clf, params=params)


if __name__ == '__main__':
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    train_tests()
    # load_test()