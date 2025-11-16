"""Comprehensive tests for main.py module.

This test module demonstrates:
- Unit testing with pytest
- Async testing with pytest-asyncio
- Type-safe test code that passes MyPy and Pyright
- Fixtures for test data setup
- Parametrized tests for multiple scenarios
"""

import asyncio
from typing import Any

import pytest

from main import (
    Container,
    add_numbers,
    calculate_average,
    compare_values,
    get_user_age,
    greet,
    merge_configs,
    number_generator,
    process_value,
)


# Unit tests for synchronous functions
@pytest.mark.unit
class TestBasicFunctions:
    """Test basic arithmetic and string functions."""

    def test_add_numbers_positive(self) -> None:
        """Test adding two positive integers."""
        result = add_numbers(5, 3)
        assert result == 8

    def test_add_numbers_negative(self) -> None:
        """Test adding negative integers."""
        result = add_numbers(-5, -3)
        assert result == -8

    def test_add_numbers_mixed(self) -> None:
        """Test adding positive and negative integers."""
        result = add_numbers(10, -3)
        assert result == 7

    def test_add_numbers_zero(self) -> None:
        """Test adding with zero."""
        result = add_numbers(0, 0)
        assert result == 0


@pytest.mark.unit
class TestGreetFunction:
    """Test greeting message generation."""

    def test_greet_with_name(self) -> None:
        """Test greeting with a specific name."""
        result = greet("Alice")
        assert result == "Hello, Alice!"

    def test_greet_without_name(self) -> None:
        """Test default greeting."""
        result = greet()
        assert result == "Hello, World!"

    def test_greet_with_none(self) -> None:
        """Test greeting with explicit None."""
        result = greet(None)
        assert result == "Hello, World!"

    def test_greet_empty_string(self) -> None:
        """Test greeting with empty string."""
        result = greet("")
        assert result == "Hello, !"


@pytest.mark.unit
class TestProcessValue:
    """Test union type value processing."""

    def test_process_value_integer(self) -> None:
        """Test processing integer value."""
        result = process_value(42)
        assert result == "Number: 42"

    def test_process_value_string(self) -> None:
        """Test processing string value."""
        result = process_value("hello")
        assert result == "Text: hello"

    def test_process_value_negative_int(self) -> None:
        """Test processing negative integer."""
        result = process_value(-100)
        assert result == "Number: -100"


@pytest.mark.unit
class TestCalculateAverage:
    """Test average calculation."""

    def test_calculate_average_positive_numbers(self) -> None:
        """Test average of positive numbers."""
        result = calculate_average([1.0, 2.0, 3.0, 4.0, 5.0])
        assert result == 3.0

    def test_calculate_average_single_number(self) -> None:
        """Test average of single number."""
        result = calculate_average([42.0])
        assert result == 42.0

    def test_calculate_average_decimals(self) -> None:
        """Test average with decimal numbers."""
        result = calculate_average([1.5, 2.5, 3.5])
        assert result == 2.5

    def test_calculate_average_empty_list_raises_error(self) -> None:
        """Test that empty list raises ValueError."""
        with pytest.raises(ValueError, match="Cannot calculate average of empty list"):
            _ = calculate_average([])


@pytest.mark.unit
class TestMergeConfigs:
    """Test configuration dictionary merging."""

    def test_merge_configs_no_overlap(self) -> None:
        """Test merging configs with no overlapping keys."""
        base = {"timeout": 30, "retries": 3}
        override = {"workers": 4, "verbose": 1}
        result = merge_configs(base, override)
        assert result == {"timeout": 30, "retries": 3, "workers": 4, "verbose": 1}

    def test_merge_configs_with_overlap(self) -> None:
        """Test merging configs with overlapping keys."""
        base = {"timeout": 30, "retries": 3}
        override = {"retries": 5, "workers": 4}
        result = merge_configs(base, override)
        assert result == {"timeout": 30, "retries": 5, "workers": 4}

    def test_merge_configs_empty_base(self) -> None:
        """Test merging with empty base config."""
        base: dict[str, int] = {}
        override = {"workers": 4}
        result = merge_configs(base, override)
        assert result == {"workers": 4}

    def test_merge_configs_empty_override(self) -> None:
        """Test merging with empty override config."""
        base = {"timeout": 30}
        override: dict[str, int] = {}
        result = merge_configs(base, override)
        assert result == {"timeout": 30}


@pytest.mark.unit
class TestContainer:
    """Test generic container class."""

    def test_container_init_and_get(self) -> None:
        """Test container initialization and value retrieval."""
        container: Container[int] = Container(42)
        assert container.get() == 42

    def test_container_set(self) -> None:
        """Test container value setting."""
        container: Container[str] = Container("initial")
        container.set("updated")
        assert container.get() == "updated"

    def test_container_with_list(self) -> None:
        """Test container with list type."""
        container: Container[list[int]] = Container([1, 2, 3])
        assert container.get() == [1, 2, 3]

    def test_container_with_dict(self) -> None:
        """Test container with dict type."""
        data = {"key": "value"}
        container: Container[dict[str, str]] = Container(data)
        assert container.get() == {"key": "value"}


@pytest.mark.unit
class TestCompareValues:
    """Test integer comparison."""

    def test_compare_values_equal(self) -> None:
        """Test comparison of equal values."""
        assert compare_values(10, 10) is True

    def test_compare_values_not_equal(self) -> None:
        """Test comparison of unequal values."""
        assert compare_values(10, 20) is False

    def test_compare_values_negative(self) -> None:
        """Test comparison with negative numbers."""
        assert compare_values(-5, -5) is True


@pytest.mark.unit
class TestGetUserAge:
    """Test user age extraction."""

    def test_get_user_age_valid(self) -> None:
        """Test extracting valid user age."""
        user_data = {"name": "Alice", "age": 30}
        assert get_user_age(user_data) == 30

    def test_get_user_age_missing_key(self) -> None:
        """Test that missing age key raises KeyError."""
        user_data: dict[str, Any] = {"name": "Alice"}
        with pytest.raises(KeyError):
            _ = get_user_age(user_data)

    def test_get_user_age_wrong_type(self) -> None:
        """Test that non-integer age raises TypeError."""
        user_data: dict[str, Any] = {"age": "thirty"}
        with pytest.raises(TypeError, match="Age must be an integer"):
            _ = get_user_age(user_data)


@pytest.mark.unit
class TestNumberGenerator:
    """Test generator function."""

    def test_number_generator_range(self) -> None:
        """Test generator produces correct range."""
        result = list(number_generator(1, 5))
        assert result == [1, 2, 3, 4, 5]

    def test_number_generator_single(self) -> None:
        """Test generator with single number."""
        result = list(number_generator(5, 5))
        assert result == [5]

    def test_number_generator_negative_range(self) -> None:
        """Test generator with negative numbers."""
        result = list(number_generator(-2, 2))
        assert result == [-2, -1, 0, 1, 2]


# Parametrized tests for comprehensive coverage
@pytest.mark.unit
class TestParametrizedTests:
    """Demonstrate parametrized testing."""

    @pytest.mark.parametrize(
        "a,b,expected",
        [
            (0, 0, 0),
            (1, 1, 2),
            (10, 20, 30),
            (-5, 5, 0),
            (100, -50, 50),
        ],
    )
    def test_add_numbers_parametrized(self, a: int, b: int, expected: int) -> None:
        """Parametrized test for add_numbers."""
        assert add_numbers(a, b) == expected

    @pytest.mark.parametrize(
        "name,expected",
        [
            ("Alice", "Hello, Alice!"),
            ("Bob", "Hello, Bob!"),
            ("", "Hello, !"),
        ],
    )
    def test_greet_parametrized(self, name: str, expected: str) -> None:
        """Parametrized test for greet."""
        assert greet(name) == expected


# Async tests to demonstrate pytest-asyncio
@pytest.mark.asyncio
async def test_async_add_numbers() -> None:
    """Async test for add_numbers (demonstrates async testing)."""
    await asyncio.sleep(0.001)  # Simulate async operation
    result = add_numbers(10, 20)
    assert result == 30


@pytest.mark.asyncio
async def test_async_greet() -> None:
    """Async test for greet function."""
    await asyncio.sleep(0.001)  # Simulate async operation
    result = greet("AsyncWorld")
    assert result == "Hello, AsyncWorld!"


@pytest.mark.asyncio
async def test_async_calculate_average() -> None:
    """Async test for calculate_average."""
    await asyncio.sleep(0.001)  # Simulate async operation
    numbers = [2.0, 4.0, 6.0, 8.0, 10.0]
    result = calculate_average(numbers)
    assert result == 6.0


# Fixture examples
@pytest.fixture
def sample_user_data() -> dict[str, Any]:
    """Fixture providing sample user data."""
    return {"name": "TestUser", "age": 25, "email": "test@example.com"}


@pytest.fixture
def sample_config() -> dict[str, int]:
    """Fixture providing sample configuration."""
    return {"timeout": 60, "retries": 5, "workers": 2}


@pytest.mark.unit
def test_with_user_fixture(sample_user_data: dict[str, Any]) -> None:
    """Test using user data fixture."""
    age = get_user_age(sample_user_data)
    assert age == 25


@pytest.mark.unit
def test_with_config_fixture(sample_config: dict[str, int]) -> None:
    """Test using config fixture."""
    override = {"workers": 10}
    result = merge_configs(sample_config, override)
    assert result["workers"] == 10
    assert result["timeout"] == 60


# Integration-style test
@pytest.mark.integration
async def test_multiple_operations_integration() -> None:
    """Integration test combining multiple operations."""
    # Test multiple functions together
    sum_result = add_numbers(5, 10)
    greeting = greet("Integration")
    average = calculate_average([float(sum_result), 20.0, 25.0])

    assert sum_result == 15
    assert greeting == "Hello, Integration!"
    assert average == 20.0

    # Simulate async operation
    await asyncio.sleep(0.001)


# Test main function execution
@pytest.mark.integration
def test_main_function(capsys: pytest.CaptureFixture[str]) -> None:
    """Test main function executes without errors."""
    from main import main

    # Run main and capture output
    main()

    # Verify output was produced
    captured = capsys.readouterr()
    assert "5 + 3 = 8" in captured.out
    assert "Hello, World!" in captured.out
    assert "Hello, Python!" in captured.out
    assert "Number: 42" in captured.out
    assert "Text: hello" in captured.out
    assert "Average: 3.0" in captured.out
    assert "Container value: 42" in captured.out
    assert "Updated value: 100" in captured.out
    assert "10 == 10: True" in captured.out
    assert "User age: 30" in captured.out
    assert "Numbers 1-5:" in captured.out
