import numpy as np

def prob_to_label(prob):
    return prob.argmax(axis=-1)


def abs_error(predicted, actual):
    return np.absolute(actual-predicted[:len(actual)])


def mean_abs_error(predicted, actual):
    absolute_error = abs_error(predicted, actual)
    return absolute_error.mean(axis=-1)
