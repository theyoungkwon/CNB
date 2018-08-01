import matplotlib.pyplot as plt
from drawnow import drawnow

from ExpApp.Utils.constants import CHANNELS_NUMBER
from ExpApp.tests.read_sample import ReadSample


def print_data(sample):
    print("----------------")
    print("%f" % (sample.id))
    print(sample.channel_data)
    print(sample.aux_data)
    print("----------------")


x = list()
y = list()
count = 1

def make_fig():
    # f, subplots = plt.subplots(CHANNELS_NUMBER, sharex=True)
    for i in range(CHANNELS_NUMBER):
        if len(y) > 0:
            plt.subplot(CHANNELS_NUMBER * 100 + 10 + i + 1)
            # subplots[i].plot(x, [row[i] for row in y])
            plt.plot(x, [row[i] for row in y])


def plot_data(sample):
    if 0 != sample.id:
        global count
        x.append(count)
        y.append(sample.channel_data)
        drawnow(make_fig)
        count = count + 1


if __name__ == '__main__':
    # board = Connector()
    # board.attach_handlers([plot_data])

    reader = ReadSample()
    sample = reader.read_sample()
    while sample is not None:
        # time.sleep(1. / 255.)
        plot_data(sample)
        sample = reader.read_sample()

    plt.ion()
    plt.show()
