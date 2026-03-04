import time
import functools
import logging

logger = logging.getLogger(__name__)

def timer_benchmark(func):
    """Decorator that prints the execution time of the function it decorates."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        duration = end_time - start_time
        logger.info(f"⏱️  {func.__name__} took {duration:.2f} seconds to complete.")
        return result
    return wrapper
