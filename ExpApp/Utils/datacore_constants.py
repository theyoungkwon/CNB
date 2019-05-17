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

TC_B = 100  # trial cutoff beginning
TC_E = 400  # trial cutoff end
T2T_RATIO = 0.8  # train to test ratio

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
