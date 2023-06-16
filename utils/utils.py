from queue import Queue
import multiprocessing as mp

def clear_queue(queue):
    while not queue.empty():
        queue.get()