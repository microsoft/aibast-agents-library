"""
Result Type for Explicit Error Handling

A minimal, pragmatic Result type that surfaces failures instead of silently
swallowing them. Based on functional programming patterns but kept simple
for Python.

Usage:
    from utils.result import Result, Success, Failure

    def load_something() -> Result[MyData, str]:
        try:
            data = do_risky_thing()
            return Success(data)
        except Exception as e:
            return Failure(f"Failed to load: {e}")

    # Using the result
    result = load_something()
    if result.is_success:
        print(result.value)
    else:
        print(f"Error: {result.error}")

    # Or with fold
    message = result.fold(
        on_failure=lambda e: f"Error: {e}",
        on_success=lambda v: f"Got: {v}"
    )
"""

from dataclasses import dataclass
from typing import TypeVar, Generic, Callable, List, Tuple, Optional, Union

T = TypeVar('T')  # Success value type
E = TypeVar('E')  # Error type
U = TypeVar('U')  # Transformed type


@dataclass(frozen=True)
class Success(Generic[T]):
    """Represents a successful result containing a value."""
    value: T

    @property
    def is_success(self) -> bool:
        return True

    @property
    def is_failure(self) -> bool:
        return False

    def map(self, f: Callable[[T], U]) -> 'Result[U, E]':
        """Transform the success value."""
        return Success(f(self.value))

    def flat_map(self, f: Callable[[T], 'Result[U, E]']) -> 'Result[U, E]':
        """Chain another Result-returning operation."""
        return f(self.value)

    def get_or_else(self, default: T) -> T:
        """Return the value (ignores default)."""
        return self.value

    def fold(self, on_failure: Callable[[E], U], on_success: Callable[[T], U]) -> U:
        """Extract value by handling both cases."""
        return on_success(self.value)

    def __repr__(self) -> str:
        return f"Success({self.value!r})"


@dataclass(frozen=True)
class Failure(Generic[E]):
    """Represents a failed result containing an error."""
    error: E

    @property
    def is_success(self) -> bool:
        return False

    @property
    def is_failure(self) -> bool:
        return True

    def map(self, f: Callable) -> 'Result[T, E]':
        """No-op for Failure - error passes through."""
        return self

    def flat_map(self, f: Callable) -> 'Result[T, E]':
        """No-op for Failure - error passes through."""
        return self

    def get_or_else(self, default: T) -> T:
        """Return the default value."""
        return default

    def fold(self, on_failure: Callable[[E], U], on_success: Callable[[T], U]) -> U:
        """Extract value by handling both cases."""
        return on_failure(self.error)

    def __repr__(self) -> str:
        return f"Failure({self.error!r})"


# Type alias for Result
Result = Union[Success[T], Failure[E]]


# --- Typed Error Classes ---

@dataclass(frozen=True)
class AgentLoadError:
    """Error that occurred while loading an agent."""
    agent_name: str
    source: str  # 'local', 'azure', 'multi_agents'
    error_type: str  # 'import', 'syntax', 'instantiation', 'no_class', 'file_read'
    message: str

    def __str__(self) -> str:
        return f"[{self.source}] {self.agent_name}: {self.error_type} - {self.message}"


@dataclass(frozen=True)
class APIError:
    """Error from OpenAI API call."""
    error_type: str  # 'rate_limit', 'auth', 'timeout', 'invalid_request', 'server', 'unknown'
    message: str
    status_code: Optional[int] = None
    retryable: bool = False

    def __str__(self) -> str:
        code = f" ({self.status_code})" if self.status_code else ""
        retry = " [retryable]" if self.retryable else ""
        return f"{self.error_type}{code}: {self.message}{retry}"


# --- Utility Functions ---

def partition_results(
    results: List[Result[T, E]]
) -> Tuple[List[T], List[E]]:
    """
    Partition a list of Results into successes and failures.

    Returns:
        Tuple of (success_values, errors)
    """
    successes = []
    failures = []

    for result in results:
        if isinstance(result, Success):
            successes.append(result.value)
        else:
            failures.append(result.error)

    return successes, failures


def sequence_results(results: List[Result[T, E]]) -> Result[List[T], List[E]]:
    """
    Convert List[Result[T, E]] to Result[List[T], List[E]].

    If all succeed: Success with list of values
    If any fail: Failure with list of all errors
    """
    successes, failures = partition_results(results)

    if failures:
        return Failure(failures)
    return Success(successes)


def try_result(f: Callable[[], T], error_mapper: Callable[[Exception], E]) -> Result[T, E]:
    """
    Execute a function and wrap the result.

    Usage:
        result = try_result(
            lambda: risky_operation(),
            lambda e: f"Operation failed: {e}"
        )
    """
    try:
        return Success(f())
    except Exception as e:
        return Failure(error_mapper(e))
