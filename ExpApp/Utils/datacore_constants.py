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
    "00000",  # palm
    "11111",  # fist
    "10000",  # thumb
    "01000",  # point
    "10100",  # respect
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
    "point",
    "two",
    "three",
    "palm"
]

BUZZ_SET = [
    "00000",  # palm
    "11111",  # fist
    "10000",  # thumb
    "01000",  # point
    "10100",  # respect
]

TC_B = 100  # trial cutoff beginning
TC_E = 400  # trial cutoff end
C_INTERVAL = 40  # classification interval every C_INTERVAL samples
KERAS_BATCH_SIZE = 5
KERAS_EPOCHS = 8
RT_OVERLAP = 0.5
RT_LAG = 0
EMG_MAX = 128.


def scale_input(x):
    x /= EMG_MAX
    return x


WINDOW_LENGTHS = [
    50,
    100,
    125,
    150
]


class KeyboardControl:
    MAX_SUGGESTION_VOTES = 2
    MAX_VOTES = 2

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
        ["p", "<", "<"],
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


PARTICIPANT_LIST = [
    "kirill_nb",

    "kirillpen",
    "kirillumbr2",
    "kirill",

    "yolpen",
    "yolumbr",
    "yol",

    "yal",
    "yalpen",
    "yalumbr",

    "moinumbr",
    "moinpen",
    "moin",

    "arthur",
    "arthurumbr",
    "arthurpen",

    "serkanumbr",
    "serkanpen",
    "serkan",

    "carlosumbr",
    "carlos",
    "carlospen",

    "panosumbr",
    "panospen",
    "panos",

    "vlasis",
    "vlasispen",
    "vlasisumbr",

    "ehsan",
    "ehsanpen",
    "ehsanumbr",

    "young",
    "youngpen",
    "youngumbr",

    "paulumbr",
    "paulpen",
    "paul",

    "kirillpen",
]
