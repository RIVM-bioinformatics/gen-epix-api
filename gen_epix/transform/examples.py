"""
Examples demonstrating usage of the transformer framework.
"""

from pydantic import BaseModel

from gen_epix.transform import (
    ConditionalTransformer,
    FieldTransformer,
    ObjectAdapter,
    Pipeline,
    StreamingPipeline,
    ValidationTransformer,
    register_transformer,
)
from gen_epix.transform.transformer import Transformer


class Person(BaseModel):
    """Example Pydantic model."""

    name: str
    age: int
    email: str


@register_transformer("string_upper")
class StringUpperTransformer(Transformer):
    """Example custom transformer."""

    def __init__(self, name: str = "StringUpperTransformer"):
        super().__init__(name)

    def transform(self, obj: ObjectAdapter) -> ObjectAdapter:
        # This would need to implement the actual transformation
        return obj


def example_usage() -> None:
    """Demonstrate basic usage of the transformer framework."""

    # Sample data - mix of dict and Pydantic models
    data = [
        {"name": "john doe", "age": 30, "email": "JOHN@EXAMPLE.COM"},
        {"name": "jane smith", "age": 25, "email": "jane@EXAMPLE.com"},
        Person(name="bob wilson", age=35, email="BOB@example.COM"),
    ]

    # Create transformers
    name_normalizer = FieldTransformer(
        field_name="name", transform_fn=lambda x: str(x).title(), name="NameNormalizer"
    )

    email_normalizer = FieldTransformer(
        field_name="email",
        transform_fn=lambda x: str(x).lower(),
        name="EmailNormalizer",
    )

    age_validator = ValidationTransformer(
        validator=lambda obj: obj.get("age", 0) > 0, name="AgeValidator"
    )

    # Create pipeline
    pipeline = Pipeline([age_validator, name_normalizer, email_normalizer])

    # Process data
    streaming_pipeline = StreamingPipeline(pipeline)
    successes, errors = streaming_pipeline.collect_errors(iter(data))

    print(f"Successfully processed {len(successes)} objects")
    print(f"Failed to process {len(errors)} objects")

    for success in successes:
        print(f"Success: {success}")

    for error in errors:
        print(f"Error: {error}")


def example_conditional_transformation() -> None:
    """Demonstrate conditional transformation."""

    data = [
        {"name": "John", "country": "US", "phone": "1234567890"},
        {"name": "Alice", "country": "UK", "phone": "9876543210"},
    ]

    # Phone normalization only for US numbers
    us_phone_normalizer = ConditionalTransformer(
        condition=lambda obj: obj.get("country") == "US",
        transformer=FieldTransformer(
            field_name="phone", transform_fn=lambda x: f"+1-{x[:3]}-{x[3:6]}-{x[6:]}"
        ),
        name="USPhoneNormalizer",
    )

    pipeline = Pipeline([us_phone_normalizer])

    for result in pipeline.process_stream(iter(data)):
        if result.success:
            print(f"Transformed: {result.transformed_object}")
        else:
            print(f"Failed: {result.error}")


if __name__ == "__main__":
    print("=== Basic Usage ===")
    example_usage()

    print("\n=== Conditional Transformation ===")
    example_conditional_transformation()
