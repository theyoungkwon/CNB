import tensorflow as tf
from tensorflow.contrib.layers import xavier_initializer

from ExpApp.Utils.datacore_constants import Layer, IMG_X, IMG_Y, LEARNING_RATE, MOMENTUM, BATCH_SIZE, STEPS, NUM_LABELS, \
    label_to_gesture, TC_B, TC_E

cnn_config = [
    Layer(25, [1, 10], 1),
    Layer(25, [2, 25], 2),
    Layer(50, [10, 25], 1),
    Layer(100, [10, 50], 2),
    Layer(200, [10, 100], 1)
]

DENSE_UNITS = 1024


class EMG_CNN:
    @staticmethod
    def build_cnn(features, wl=IMG_Y):
        # Input layer
        input_layer = tf.reshape(features["x"], [-1, IMG_X, wl, 1])

        # Convolution layers
        for layer in cnn_config:
            # Convolution
            input_layer = tf.layers.conv2d(
                kernel_initializer=xavier_initializer(seed=42),
                kernel_size=layer.filter_size,
                activation=tf.nn.relu,
                filters=layer.filters,
                strides=layer.stride,
                inputs=input_layer,
                padding="same",
            )

        # FC Layer
        shrinkage = 1
        for layer in cnn_config:
            shrinkage = shrinkage * layer.stride

        il_filters = cnn_config[len(cnn_config) - 1].filters
        il_dim_x = IMG_X // shrinkage
        il_dim_y = wl // shrinkage
        input_layer = tf.reshape(input_layer, [-1, il_dim_x * il_dim_y * il_filters])

        input_layer = tf.layers.dense(
            kernel_initializer=xavier_initializer(seed=42),
            activation=tf.nn.relu,
            inputs=input_layer,
            units=DENSE_UNITS,
        )

        # Logits layer
        logits = tf.layers.dense(inputs=input_layer, units=NUM_LABELS)

        return logits, input_layer

    @staticmethod
    def cnn_model_fn(features, labels, mode, params):
        learning_rate = LEARNING_RATE
        if "learning_rate" in params:
            learning_rate = params["learning_rate"]

        momentum = MOMENTUM
        if "momentum" in params:
            momentum = params["momentum"]

        start = TC_B
        if "start" in params:
            start = params["start"]

        end = TC_E
        if "end" in params:
            end = params["end"]
        wl = end - start

        logits, input_layer = EMG_CNN.build_cnn(features, wl)

        # Output
        predictions = {
            "classes": tf.argmax(input=logits, axis=1),
            "probabilities": tf.nn.softmax(input_layer, name="softmax_tensor"),
        }

        # PREDICT
        if mode == tf.estimator.ModeKeys.PREDICT:
            return tf.estimator.EstimatorSpec(mode=mode, predictions=predictions)

        loss = tf.losses.sparse_softmax_cross_entropy(labels=labels, logits=logits)

        # TRAIN
        if mode == tf.estimator.ModeKeys.TRAIN:
            optimizer = tf.train.MomentumOptimizer(learning_rate=learning_rate, momentum=momentum)

            train_op = optimizer.minimize(
                loss=loss,
                global_step=tf.train.get_global_step())
            return tf.estimator.EstimatorSpec(mode=mode, loss=loss, train_op=train_op)

        # EVAL
        eval_metric_ops = {
            "accuracy": tf.metrics.accuracy(labels=labels, predictions=predictions["classes"])
        }
        return tf.estimator.EstimatorSpec(
            mode=mode, loss=loss, eval_metric_ops=eval_metric_ops)

    @staticmethod
    def load(model_dir="EMG/", params={}):
        return tf.estimator.Estimator(
            model_fn=EMG_CNN.cnn_model_fn,
            model_dir="./models/" + model_dir,
            params=params
        )

    @staticmethod
    def train(input_fn, model_dir="EMG/", params={}):
        # CREATE
        classifier = tf.estimator.Estimator(
            model_fn=EMG_CNN.cnn_model_fn,
            model_dir="./models/" + model_dir,
            params=params
        )

        steps = STEPS
        if "steps" in params:
            steps = params["steps"]

        # TRAIN
        data, labels = input_fn(test=False, params=params)
        train_input_fn_1 = tf.estimator.inputs.numpy_input_fn(
            x={"x": data},
            y=labels,
            batch_size=BATCH_SIZE,
            num_epochs=None,
            shuffle=True)
        classifier.train(
            input_fn=train_input_fn_1,
            steps=steps)
        return classifier

    @staticmethod
    def test(clf, input_fn, params={}):
        # TEST
        data, labels = input_fn(test=True, params=params)
        eval_input_fn = tf.estimator.inputs.numpy_input_fn(
            x={"x": data},
            y=labels,
            num_epochs=2,
            shuffle=False)

        # ACCURACY REPORT
        accuracy = clf.evaluate(
            input_fn=eval_input_fn)
        print(accuracy)

    @staticmethod
    def predict(clf, input_fn):
        # TEST
        data, labels = input_fn(test=True)
        eval_input_fn = tf.estimator.inputs.numpy_input_fn(
            x={"x": data},
            num_epochs=2,
            shuffle=False)
        predictions = clf.predict(
            input_fn=eval_input_fn)
        for prediction in predictions:
            print(label_to_gesture(prediction['classes']))

    @staticmethod
    def export(in_dir, out_dir, params):
        clf = tf.estimator.Estimator(
            model_fn=EMG_CNN.cnn_model_fn,
            model_dir="./models/" + in_dir,
            params=params
        )
        clf.export_savedmodel(export_dir_base=out_dir, serving_input_receiver_fn=None)
