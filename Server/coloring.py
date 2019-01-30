# import colors as c
# print(c.red("hello"), c.blue("world"))

import sys

COLORS = {
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m"
}

END = "\033[0m"
def cyan(self):
    raise NotImplementedError
def red(self):
    raise NotImplementedError
def green(self):
    raise NotImplementedError


def make(name, code):
    def f(*strings):
        return "".join([code, " ".join(map(str, strings)), END])
    return f


for name, code in COLORS.items():
    setattr(sys.modules[__name__], name, make(name, code))