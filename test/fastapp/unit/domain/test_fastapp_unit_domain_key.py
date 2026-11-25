"""Verify key generation from ordinary and computed Pydantic fields."""

from pydantic import BaseModel, computed_field

from gen_epix.fastapp.domain.key import Key


class ModelWithComputedField(BaseModel):
    """Model exposing a derived value as a Pydantic computed field."""

    code: str

    @computed_field
    @property
    def normalized_code(self) -> str:
        """Return the normalized code used for key generation."""
        return self.code.lower()


def test_key_generator_reads_computed_field() -> None:
    """Generate a key using a computed model attribute absent from __dict__."""
    model = ModelWithComputedField(code="ABC")

    assert Key("normalized_code")(model) == "abc"
