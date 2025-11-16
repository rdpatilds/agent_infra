"""MyPy type checking test suite.

This module tests various MyPy strict mode configurations to ensure
proper type checking is enforced across the codebase.
"""

from collections.abc import Generator
from typing import Any


# Test 1: Properly typed function (should pass)
def add_numbers(a: int, b: int) -> int:
    """Add two integers together.

    Args:
        a: First integer
        b: Second integer

    Returns:
        Sum of a and b
    """
    return a + b


# Test 2: Function with Optional parameter (should pass)
def greet(name: str | None = None) -> str:
    """Generate a greeting message.

    Args:
        name: Optional name to greet

    Returns:
        Greeting string
    """
    if name is None:
        return "Hello, World!"
    return f"Hello, {name}!"


# Test 3: Function with Union types (should pass)
def process_value(value: int | str) -> str:
    """Process a value that can be int or str.

    Args:
        value: Integer or string value

    Returns:
        String representation
    """
    if isinstance(value, int):
        return f"Number: {value}"
    return f"Text: {value}"


# Test 4: Function with list type annotations (should pass)
def calculate_average(numbers: list[float]) -> float:
    """Calculate the average of a list of numbers.

    Args:
        numbers: List of numbers

    Returns:
        Average value

    Raises:
        ValueError: If list is empty
    """
    if not numbers:
        raise ValueError("Cannot calculate average of empty list")
    return sum(numbers) / len(numbers)


# Test 5: Function with dict type annotations (should pass)
def merge_configs(
    base_config: dict[str, int], override_config: dict[str, int]
) -> dict[str, int]:
    """Merge two configuration dictionaries.

    Args:
        base_config: Base configuration
        override_config: Override configuration

    Returns:
        Merged configuration
    """
    result = base_config.copy()
    result.update(override_config)
    return result


# Test 6: Generic class (should pass)
class Container[T]:
    """Generic container class.

    Type Parameters:
        T: Type of items stored in container
    """

    def __init__(self, value: T) -> None:
        """Initialize container with a value.

        Args:
            value: Initial value
        """
        super().__init__()
        self.value: T = value

    def get(self) -> T:
        """Get the stored value.

        Returns:
            Stored value
        """
        return self.value

    def set(self, value: T) -> None:
        """Set a new value.

        Args:
            value: New value to store
        """
        self.value = value


# Test 7: Function testing strict equality (should pass)
def compare_values(a: int, b: int) -> bool:
    """Compare two integers.

    Args:
        a: First integer
        b: Second integer

    Returns:
        True if equal, False otherwise
    """
    return a == b


# Test 8: Function with explicit return type checking
def get_user_age(user_data: dict[str, Any]) -> int:
    """Extract user age from data dictionary.

    Args:
        user_data: Dictionary containing user information

    Returns:
        User's age

    Raises:
        KeyError: If age key is missing
        TypeError: If age is not an integer
    """
    age = user_data["age"]
    if not isinstance(age, int):
        raise TypeError("Age must be an integer")
    return age


# Test 9: Generator function with proper types
def number_generator(start: int, end: int) -> Generator[int, None, None]:
    """Generate numbers from start to end.

    Args:
        start: Starting number
        end: Ending number (inclusive)

    Yields:
        Numbers from start to end
    """
    yield from range(start, end + 1)


def main() -> None:
    """Main entry point demonstrating type-safe code."""
    # Test basic operations
    result = add_numbers(5, 3)
    print(f"5 + 3 = {result}")

    # Test optional parameters
    print(greet())
    print(greet("Python"))

    # Test union types
    print(process_value(42))
    print(process_value("hello"))

    # Test list operations
    nums = [1.0, 2.0, 3.0, 4.0, 5.0]
    avg = calculate_average(nums)
    print(f"Average: {avg}")

    # Test dict operations
    config1 = {"timeout": 30, "retries": 3}
    config2 = {"retries": 5, "workers": 4}
    merged = merge_configs(config1, config2)
    print(f"Merged config: {merged}")

    # Test generic container
    int_container: Container[int] = Container(42)
    print(f"Container value: {int_container.get()}")
    int_container.set(100)
    print(f"Updated value: {int_container.get()}")

    # Test comparison
    is_equal = compare_values(10, 10)
    print(f"10 == 10: {is_equal}")

    # Test user data extraction
    user = {"name": "Alice", "age": 30, "email": "alice@example.com"}
    age = get_user_age(user)
    print(f"User age: {age}")

    # Test generator
    print("Numbers 1-5:", end=" ")
    for num in number_generator(1, 5):
        print(num, end=" ")
    print()


if __name__ == "__main__":
    main()
