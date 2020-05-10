import numpy as np
import tempfile
import math
import os
import matplotlib.pyplot as plt
from contextlib import contextmanager

from .roller import distr


def weighted_avg_and_std(values, weights):
    """
    Return the weighted average and standard deviation.

    values, weights -- Numpy ndarrays with the same shape.
    """
    average = np.average(values, weights=weights)
    # Fast and numerically precise:
    variance = np.average((values-average)**2, weights=weights)
    return (average, math.sqrt(variance))


@contextmanager
def bake_distribution(txt, env):
    rolls = distr(txt, env)

    sumw = sum(a*b for a, b in zip(rolls[0], rolls[1]))

    amounts = list(int(r) for r in rolls[0])
    weights = list(r / float(sumw) for r in rolls[1])
    am = len(np.unique(amounts))

    avg, std = weighted_avg_and_std(amounts, weights)

    plt.hist(amounts, weights=weights, bins=am, color="#d80404", zorder=1)
    plt.hist(amounts, weights=weights, bins=am, color="#7f0707", zorder=2, histtype='step')
    plt.ylabel("Probability")
    plt.xlabel("Roll total, average: {}±{}".format(round(avg, 5), round(std, 5)))
    plt.title("Distribution of " + txt)

    file = tempfile.NamedTemporaryFile(delete=False)
    plt.savefig(file, format="png")
    plt.clf()
    name = file.name
    file.close()
    yield name
    os.remove(file.name)
