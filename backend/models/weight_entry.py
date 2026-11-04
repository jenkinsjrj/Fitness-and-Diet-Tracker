"""Body-weight history model and validation rules."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Union


WeightValue = Union[Decimal, int, float]


@dataclass
class WeightEntry:
    """One body-weight measurement, stored internally in kilograms."""

    user_id: int
    weight_kg: WeightValue
    recorded_date: date

    def validate(self) -> None:
        """Normalize weight to Decimal and enforce the SQL column's limits."""
        if type(self.user_id) is not int or self.user_id <= 0:
            raise ValueError("Invalid user ID")

        if isinstance(self.weight_kg, bool) or not isinstance(
            self.weight_kg, (Decimal, int, float)
        ):
            raise ValueError("Weight must be a number in kilograms")

        try:
            value = Decimal(str(self.weight_kg))
        except (InvalidOperation, ValueError):
            raise ValueError("Weight must be a valid number") from None

        if not value.is_finite():
            raise ValueError("Weight must be a finite number")
        if value <= 0:
            raise ValueError("Weight must be positive")
        # schema.sql defines DECIMAL(5,2), so at most 999.99 kg can be stored.
        if value > Decimal("999.99"):
            raise ValueError("Weight must be 999.99 kg or less")
        if value != value.quantize(Decimal("0.01")):
            raise ValueError("Weight may have at most two decimal places")

        self.weight_kg = value

        if type(self.recorded_date) is not date:
            raise ValueError("Recorded date must be a valid date")
