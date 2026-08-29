import datetime
from uuid import uuid4

from gen_epix.casedb.domain.model.case.case_data import Case
from gen_epix.casedb.services.case.case_date import (
    case_service_calculate_case_date,
    convert_iso_date_to_datetime,
    convert_iso_week_to_first_day_datetime,
)


class TestGetCaseDate:
    """Unit tests for case_service_calculate_case_date() function."""

    def _make_case(self, content: dict) -> Case:
        return Case(
            id=uuid4(),
            case_type_id=uuid4(),
            created_in_data_collection_id=uuid4(),
            content=content,
        )

    def test_stops_at_highest_resolution_when_both_day_and_week_present(self) -> None:
        day_col_id = uuid4()
        week_col_id = uuid4()
        # Mapper dict ordered by descending resolution (day before week)
        col_mappers = {
            day_col_id: convert_iso_date_to_datetime,
            week_col_id: convert_iso_week_to_first_day_datetime,
        }
        case = self._make_case({day_col_id: "2024-03-15", week_col_id: "2024-W01"})
        case_service_calculate_case_date([case], col_mappers)
        # Without the break, week (2024-01-01) would overwrite day (2024-03-15)
        assert case.case_date == datetime.datetime(2024, 3, 15)

    def test_falls_back_to_lower_resolution_when_higher_is_none(self) -> None:
        day_col_id = uuid4()
        week_col_id = uuid4()
        col_mappers = {
            day_col_id: convert_iso_date_to_datetime,
            week_col_id: convert_iso_week_to_first_day_datetime,
        }
        case = self._make_case({week_col_id: "2024-W02"})
        case_service_calculate_case_date([case], col_mappers)
        assert case.case_date == datetime.datetime.fromisocalendar(2024, 2, 1)

    def test_all_cols_none_leaves_case_date_unchanged(self) -> None:
        day_col_id = uuid4()
        col_mappers = {day_col_id: convert_iso_date_to_datetime}
        case = self._make_case({})
        original_date = case.case_date
        case_service_calculate_case_date([case], col_mappers)
        assert case.case_date == original_date
