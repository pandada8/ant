import asyncio
import aiohttp


class WrongCallError(Exception):

    def __repr__(self):
        return "You should only use .init() once"


class End_Of_Life():

    def __repr__(self):
        return "[We died]"

EOL = End_Of_Life()


def iterable(obj):
    try:
        iter(obj)
        return True
    except TypeError:
        return False


class Job(object):

    def __init__(self):
        self.funcs = []
        self.loop = asyncio.get_event_loop()
        self.prev_queue = None

    def init(self, func, **kwargs):
        if len(self.funcs) == 0:
            queue = asyncio.Queue()

            def wrapper():
                result = yield from asyncio.coroutine(func)(**kwargs)
                if not iterable(result):
                    result = [result]
                for i in result:
                    yield from queue.put(i)
                yield from queue.put(EOL)  # we finished
                print('Goodbye', func.__name__)

            self.funcs.append(asyncio.coroutine(wrapper))
            self.prev_queue = queue

            return self
        else:
            raise WrongCallError

    def then(self, func, **kwargs):
        if len(self.funcs) == 0:
            raise WrongCallError

        prev_queue = self.prev_queue
        queue = asyncio.Queue()
        func = asyncio.coroutine(func)

        @asyncio.coroutine
        def wrapper():
            while True:
                print(prev_queue.empty())
                to_do = yield from prev_queue.get()
                print('recv', to_do)
                if to_do is not EOL:
                    result = yield from func(to_do, **kwargs)
                    if not iterable(result):
                        result = [result]
                    for i in result:
                        yield from queue.put(i)
                    # prev_queue.task_done()
                else:
                    yield from queue.put(EOL)
                    print("Goodbye", func.__name__)
                    return

        self.prev_queue = queue
        self.funcs.append(asyncio.coroutine(wrapper))
        return self

    def until_finish(self):
        while True:
            value = yield from self.prev_queue.get()
            # self.prev_queue.task_done()
            if value is EOL:
                return

    def run(self):
        tasks = []
        for i in self.funcs:
            tasks.append(self.loop.create_task(i()))
        self.loop.run_until_complete(self.until_finish())
        self.loop.close()


def step1():
    print('Step:1')
    return list(range(10))


def step2(x):
    print('step:2')
    return x * x


def step3(x):
    print("Step:3")
    return [x, x]

job = Job()
job.init(step1).then(step2).then(step3).run()
