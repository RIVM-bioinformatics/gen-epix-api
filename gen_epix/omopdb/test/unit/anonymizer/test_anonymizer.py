from datetime import date, datetime

from pydantic import BaseModel

from gen_epix.omopdb.services.model_anonymizer import ModelAnonymizer


class Model(BaseModel):
    str_value: str | None
    int_value: int | None
    float_value: float | None
    bool_value: bool | None
    date_value: date | None
    datetime_value: datetime | None
    list_value: list | None
    dict_value: dict | None
    tuple_value: tuple | None
    set_value: set | None
    bytes_value: bytes | None


class TestAnonymizer:
    def test_anonymize(self) -> None:
        model_anonymizer = ModelAnonymizer()
        model = Model(
            str_value="test",
            int_value=123,
            float_value=123.456,
            bool_value=True,
            date_value=date(2023, 1, 1),
            datetime_value=datetime(2023, 1, 1, 12, 0),
            list_value=["a", "b", "c"],
            dict_value={"key": "value"},
            tuple_value=("a", "b"),
            set_value={"a", "b"},
            bytes_value=b"test",
        )
        raise NotImplementedError("Test not implemented yet")
