import asyncio
import aiohttp

class WrongCallError(Exception):

    def __repr__(self):
        return "You should only use .init() once"


class Job(object):

    def __init__(self):
        self.prev_func = None
        self.prev_args = {}

    def init(self, func, **kwargs):
        if self.prev_func is None:
            self.prev_func = asyncio.coroutine(func)
            self.prev_args = kwargs if kwargs else {}

    def then(self, func, **kwargs):
        if self.prev_func is None:
            raise WrongCallError

        # we should use clousure rather the self.* in the next function, which would cause a recursion calling
        prev_func = self.prev_func
        prev_args = self.prev_args
        func = asyncio.coroutine(func)
        buffer = []  # a simple buffer here to store the data
        # @asyncio.coroutine
        def wrapper():
            result = yield from prev_func(**prev_args)
            print(result)
            if not asyncio.iscoroutine(result):
                try:
                    iter(result)
                    a = list((yield from func(i, **kwargs)) for i in result)
                    return a
                except TypeError:
                    return (yield from func(result, **kwargs))

        self.prev_args = kwargs if kwargs else {}
        self.prev_func = wrapper

    def run(self):

        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.prev_func(**self.prev_args))
        loop.close()


def step1():
    print('Step:1')
    return list(range(10))

def step2(x):
    print('step2')
    return x *x

def step3(x):
    print("Step:3")
    return [x, x]

job = Job()
job.init(step1)
job.then(step2)
job.then(step3)
job.then(print)
job.run()
