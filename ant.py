import asyncio
import aiohttp
from pyquery import PyQuery as pq
import os


class WrongCallError(Exception):

    def __repr__(self):
        return "You should call .init() only once"


class End_Of_Life():

    def __repr__(self):
        return "[We died]"

EOL = End_Of_Life()
conn = aiohttp.connector.ProxyConnector(proxy=os.getenv('HTTP_PROXY')) if os.getenv('HTTP_PROXY') else None
headers = {'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2431.0 Safari/537.36"}

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
            queue = asyncio.Queue(maxsize=10)

            def wrapper():
                if hasattr(func, "__call__"):
                    result = yield from asyncio.coroutine(func)(**kwargs)
                    if not iterable(result):
                        result = [result]
                elif iterable(func):
                    result = func
                else:
                    raise TypeError

                for i in result:
                    yield from queue.put(i)
                yield from queue.put(EOL)  # we finished

                print('Finish', func.__name__ if hasattr(func, "__call__") else "init")

            self.funcs.append(asyncio.coroutine(wrapper))
            self.prev_queue = queue

            return self
        else:
            raise WrongCallError

    def then(self, func, **kwargs):
        if len(self.funcs) == 0:
            raise WrongCallError

        prev_queue = self.prev_queue
        queue = asyncio.Queue(maxsize=10)
        func = asyncio.coroutine(func)

        @asyncio.coroutine
        def wrapper():
            while True:
                to_do = yield from prev_queue.get()
                # print(func.__name__, 'got', to_do)
                if to_do is not EOL:
                    result = yield from func(to_do, **kwargs)
                    # print(func.__name__, 'have', result)
                    if not iterable(result):
                        result = [result]
                    for i in result:
                        yield from queue.put(i)
                    # prev_queue.task_done()
                else:
                    yield from queue.put(EOL)
                    print("Finish", func.__name__)
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


def fetch_and_parse(url, **kwargs):
    kwargs['headers'] = headers
    if conn:
        kwargs['connector'] = conn
    response = yield from aiohttp.request("GET", url, **kwargs)
    # print(response)
    body = yield from response.read()
    # print(body[:100])
    return pq(body)


def fetch_and_save(url, filename, **kwargs):
    kwargs['headers'] = headers
    if conn:
        kwargs['connector'] = conn
    response = yield from aiohttp.request('GET', url, **kwargs)
    with open(filename, "wb") as fp:
        while True:
            chunk = yield from response.content.read(1024)
            if len(chunk) == 0:
                break
            fp.write(chunk)
        # ok we finish download
    return
