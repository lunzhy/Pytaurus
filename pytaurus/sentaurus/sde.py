__author__ = 'Lunzhy'
import os, sys, re
path = os.path.join(os.path.abspath(os.path.dirname(__file__)), os.pardir, os.pardir)
if not path in sys.path:
    sys.path.append(path)
import pytaurus.sentaurus as sen


def test():
    return

if __name__ == '__main__': test()