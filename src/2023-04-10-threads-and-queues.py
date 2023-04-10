import logging
from queue import Queue
from random import random
from time import sleep, time
from threading import Thread


N = 1000
MAX_TOKEN_TIME = 0.01  # Getting tokens takes longer (batching not simulated)
MAX_RESULTS_TIME = 0.005
N_TOKEN_THREADS = 10  # Use more threads for the process that takes longer
N_RESULTS_THREADS = 5

log = logging.getLogger(__name__)


def main():
    todo_queue = StoppingQueue()
    token_queue = StoppingQueue()
    results_queue = StoppingQueue()
    log.info("Start threads")
    token_threads = start_threads(N_TOKEN_THREADS, get_token, todo_queue, token_queue)
    result_threads = start_threads(N_RESULTS_THREADS, get_result, token_queue, results_queue)
    log.info("Load todo queue")
    t0 = time()
    for i in range(N):
        todo_queue.put(i)
    stop_threads(todo_queue, token_threads)
    stop_threads(token_queue, result_threads)  # Note results queue is not closed/joined
    results_queue.close()
    log.info("Getting out results")
    results = list(results_queue)
    expected = [f"result_{i}" for i in range(N)]
    log.info(f"Results: length {len(results)}, Order okay: {results == expected}")
    t1 = time()
    log.info(f"Processing took {(t1 - t0):.2f} seconds")


class StoppingQueue(Queue):
    sentinel = object()

    def close(self):
        self.put(self.sentinel)

    def __iter__(self):
        while True:
            item = self.get()
            try:
                if item is self.sentinel:
                    return
                yield item
            finally:
                self.task_done()


class StoppingWorker(Thread):
    def __init__(self, func, in_queue, out_queue):
        super().__init__()
        self.func = func
        self.in_queue = in_queue
        self.out_queue = out_queue

    def run(self):
        for item in self.in_queue:
            result = self.func(item)
            self.out_queue.put(result)


def get_token(i: int) -> str:
    sleep(random() * MAX_TOKEN_TIME)
    return f"token_{i}"


def get_result(token: str) -> str:
    sleep(random() * MAX_RESULTS_TIME)
    return token.replace("token", "result")


def start_threads(count: int, *args):
    threads = [StoppingWorker(*args) for _ in range(count)]
    for thread in threads:
        thread.start()
    return threads


def stop_threads(queue, threads):
    for _ in threads:
        queue.close()
    queue.join()
    for thread in threads:
        thread.join()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
