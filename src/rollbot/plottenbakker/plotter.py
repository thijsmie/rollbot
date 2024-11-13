import io

import matplotlib.pyplot as plt
import numpy as np


def weighted_avg_and_std(values: np.array, weights: np.array) -> tuple[float, float]:
    """
    Return the weighted average and standard deviation.

    values, weights -- Numpy ndarrays with the same shape.
    """
    average = np.average(values, weights=weights)
    # Fast and numerically precise:
    variance = np.average((values - average) ** 2, weights=weights)
    return (average, np.sqrt(variance))


def _plot_distribution(io: io.BytesIO, description: str, xbins: list[float], data: list[int]) -> None:
    fig, ax = plt.subplots()

    centroids = (np.array(xbins[1:]) + np.array(xbins[:-1])) / 2.0
    ax.hist(
        centroids,
        bins=len(data),
        weights=data,
        range=(xbins[0], xbins[-1]),
        color="#d80404",
        zorder=1,
        density=True,
    )
    ax.hist(
        centroids,
        bins=len(data),
        weights=data,
        range=(xbins[0], xbins[-1]),
        color="#7f0707",
        zorder=2,
        histtype="step",
        density=True,
    )

    astd = weighted_avg_and_std(centroids, data)
    ax.set_xlabel(f"Roll total, average: {astd[0]:.3f}±{astd[1]:.3f}")
    ax.set_title(description)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.axes.yaxis.set_visible(False)
    ax.axes.yaxis.set_ticks([])
    ax.xaxis.get_major_locator().set_params(integer=True)
    fig.tight_layout()
    fig.savefig(io, format="png")


def plot_distribution(io: io.BytesIO, expression: str, xbins: list[float], data: list[int], num_rolls: int) -> None:
    _plot_distribution(io, f"Distribution of {expression} rolled {num_rolls} times.", xbins, data)


def plot_statistics(io: io.BytesIO, description: str, stats: dict[int, int], die: int) -> None:
    _plot_distribution(
        io,
        description,
        [0.5 + i for i in range(die + 1)],
        [stats.get(i, 0) for i in range(1, die + 1)],
    )
