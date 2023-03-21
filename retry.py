import time
import sys


def give_up(ex):
    print("Giving up after multiple failures...")
    print(ex)
    sys.exit(1)


def fibonacci():
    a, b = 1, 1
    while True:
        yield a
        a, b = b, a + b


def const(i):
    while True:
        yield i


def retry(interval=const(0), max_tries=2, giveup=give_up, message="Retry.."):
    def actual_decorator(func):
        def wrapper(*args, **kwargs):
            ex = ''
            for i in range(max_tries):
                if i != 0:
                    print(message)
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    ex = e
                time.sleep(next(interval))
            giveup(ex)

        return wrapper

    return actual_decorator
