# CNN
from random import randint

BATCH_SIZE = 20
SHUFFLE_BUFFER_SIZE = 1
STEPS = 1
MOMENTUM = 0.9
LEARNING_RATE = 0.001
MAX_ITERATIONS = 1200

DENSE_DROPOUT = True
CONV_DROPOUT = True
DROPOUT_RATE = 0.5

CLASSES = [
    "fist",
    "palm",
    "thumb",
    "point",
    "two",
    "peace",
    "three",
    "four",
    "cyl_grab",
    "hcyl_grab",
    "flat_grab",
    "hflat_grab",
]

SET1 = [  # social
    "fist",
    "palm",
    "thumb",
    "point",
    "two",
]

SET2 = [  # numbers
    "point",
    "two",
    "three",
    "four",
]

SET3 = [  # force grabs
    "cyl_grab",
    "hcyl_grab",
    "flat_grab",
    "hflat_grab",
]

SET4 = [  # social + force grabs
    "fist",
    "palm",
    "thumb",
    "point",
    "two",
    "cyl_grab",
    "hcyl_grab",
    "flat_grab",
    "hflat_grab",
]

SET5 = [  # social + numbers + grabs
    "fist",
    "palm",
    "thumb",
    "point",
    "two",
    "three",
    "four",
    "cyl_grab",
    "flat_grab",
]

SET6 = [  # everything
    "fist",
    "palm",
    "thumb",
    "point",
    "two",
    "three",
    "four",
    "cyl_grab",
    "hcyl_grab",
    "flat_grab",
    "hflat_grab",
]

SET7 = [
    "fist",
    "point",
    "two",
    "three",
    "four",
]

INPUT_SET = [
    "fist",
    "thumb",
    "point",
    "two",
    "three",
    "four",
    "palm"
]

TC_B = 100  # trial cutoff beginning
TC_E = 400  # trial cutoff end
C_INTERVAL = 40  # classification interval every C_INTERVAL samples
KERAS_FRAME_LENGTH = 125  # samples in a trial
KERAS_BATCH_SIZE = 5
KERAS_EPOCHS = 7
T2T_RATIO = 0.8  # train to test ratio

class KeyboardControl:
    DELETE_VOTES_LIMIT = 5
    MAX_VOTES = 1

    configQ = [
        ["q", "a", "z"],
        ["w", "s", "x"],
        ["e", "d", "c"],
        ["r", "f", "v"],
        ["t", "g", "b"],
        ["y", "h", "n"],
        ["u", "j", "m"],
        ["i", "k", " "],
        ["o", "l", " "],
        ["p", "<", " "],
    ]

    gesture_config_def = {
        "point": 1,
        "thumb": 2,
        "two": 2,
        "three": 3,
        "four": 3,
    }


IMG_X = 8  # number if channels define the matrix width
IMG_Y = TC_E - TC_B  # matrix height

WINDOW_LENGTH_P = "window_length"


class Layer:
    filters = 0
    filter_size = [0, 0]
    stride = 1

    def __init__(self, filters, filter_size, stride):
        self.filters = filters
        self.filter_size = filter_size
        self.stride = stride


gestures = {
    "0": "FIST",
    "1": "PALM",
    "2": "THUMB",
    "3": "POINT",
    "4": "PEACE",
}


def label_to_gesture(label):
    return gestures[str(label)]


def get_random_gesture():
    return gestures[str(randint(0, len(gestures) - 1))]


class KeyConstants:
    USE_IMU = 10  # 0 (NO) or 10 (YES)
    CHANNELS_CONFIG = slice(-1)  # slice(2,4) or :(8 + KeyConstants.USE_IMU)
    BEFORE = 50
    AFTER = 20
    MODEL_PATH = "keras_keys"
    EBATCH_SIZE = 5
    ELR = 0.0001
    EEPOCHS = 10
    TOTAL_CHANNELS = 19  # 8 EMG | 10 IMU | 1 TS
    RT_LAG = 6

