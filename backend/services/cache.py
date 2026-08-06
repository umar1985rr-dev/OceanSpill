from functools import lru_cache


@lru_cache(maxsize=32)
def cached_data(data):

    return data