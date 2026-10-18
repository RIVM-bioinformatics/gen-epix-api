"""Test the executable transformation examples."""

from gen_epix.transform.examples import (
    example_conditional_transformation,
    example_usage,
)


def test_example_usage_processes_all_valid_people(capsys) -> None:
    """Report all three example inputs as successfully processed."""
    example_usage()

    output = capsys.readouterr().out
    assert "Successfully processed 3 objects" in output
    assert "Failed to process 0 objects" in output


def test_conditional_example_only_formats_us_phone_numbers(capsys) -> None:
    """Format the US phone number and preserve the non-US example value."""
    example_conditional_transformation()

    output = capsys.readouterr().out
    assert (
        "Transformed: {'name': 'John', 'country': 'US', 'phone': '+1-123-456-7890'}"
        in output
    )
    assert (
        "Transformed: {'name': 'Alice', 'country': 'UK', 'phone': '9876543210'}"
        in output
    )
    assert "Failed:" not in output
