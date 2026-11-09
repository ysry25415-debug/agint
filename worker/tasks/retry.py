"""
Retry utilities for resilient task execution.
"""

import time
import logging
from typing import Callable, Any, Dict
from functools import wraps

logger = logging.getLogger(__name__)


class RetryConfig:
    """Configuration for retry behavior."""

    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        retryable_exceptions: tuple = None,
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.retryable_exceptions = retryable_exceptions or (Exception,)


def retry(config: RetryConfig = None):
    """
    Decorator for retrying functions with exponential backoff.
    """
    if config is None:
        config = RetryConfig()

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None

            for attempt in range(config.max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except config.retryable_exceptions as e:
                    last_exception = e

                    if attempt == config.max_retries:
                        logger.error(
                            f"Final retry attempt {config.max_retries} failed for {func.__name__}"
                        )
                        raise

                    delay = min(
                        config.base_delay * (config.exponential_base ** attempt),
                        config.max_delay
                    )

                    logger.warning(
                        f"Attempt {attempt + 1} failed for {func.__name__}, "
                        f"retrying in {delay:.2f}s: {str(e)}"
                    )

                    time.sleep(delay)

            raise last_exception

        return wrapper

    return decorator


def execute_with_retry(
    func: Callable,
    task_name: str,
    max_retries: int = 3,
    base_delay: float = 1.0,
    on_retry: Callable[[int, Exception], None] = None,
) -> Any:
    """
    Execute a function with retry logic.

    Args:
        func: Function to execute
        task_name: Name of the task for logging
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay in seconds
        on_retry: Optional callback for retry events

    Returns:
        Result of the function

    Raises:
        Exception: If all retries are exhausted
    """
    attempt = 0
    last_exception = None

    while attempt <= max_retries:
        try:
            return func()
        except Exception as e:
            attempt += 1
            last_exception = e

            if attempt > max_retries:
                logger.error(f"Task {task_name} failed after {max_retries} retries: {e}")
                raise

            delay = min(base_delay * (2 ** attempt), 60.0)

            logger.warning(
                f"Task {task_name} failed on attempt {attempt}, "
                f"retrying in {delay:.2f}s: {e}"
            )

            if on_retry:
                try:
                    on_retry(attempt, e)
                except Exception as retry_error:
                    logger.warning(f"on_retry callback failed: {retry_error}")

            time.sleep(delay)

    raise last_exception