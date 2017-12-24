import sys

sys.path.insert(0, '..')
from shinobu.utilities import Logger

def divide(numerator, denominator):
    return numerator/denominator

def throw_exception():
    divide(1, 0)

if __name__ == '__main__':
    with Logger.reporter():
        throw_exception()

