"""Small input-validation helpers shared by API routes."""

from datetime import date


def parse_iso_date(value, field_name: str) -> date:
    """Parse exactly YYYY-MM-DD; reject timestamps and non-string values."""
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must use YYYY-MM-DD format")
    try:
        parsed = date.fromisoformat(value)
    except ValueError:
        raise ValueError(f"{field_name} must use YYYY-MM-DD format") from None
    if parsed.isoformat() != value:
        raise ValueError(f"{field_name} must use YYYY-MM-DD format")
    return parsed
