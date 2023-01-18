import random

def rand(): return random.randint(0, 255)
def gen_color(): return '#%02X%02X%02X' % (rand(), rand(), rand())
