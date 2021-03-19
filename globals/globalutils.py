import os, psutil


def get_last_sentence(text):
    sentences = text.split('.')
    for s in reversed(sentences):
        if s:
            return s


def get_memory():
    memory = psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2
    mem_str = str(memory) + "MB"
    return mem_str