"""Demonstrate nutrition endpoints against the running Flask app.

Read existing data:
    python scripts/demo_nutrition.py --date 2026-11-03
Also log a sample meal and then delete only that newly created meal:
    python scripts/demo_nutrition.py --date 2026-11-03 --log-sample
"""

import argparse
import json
from datetime import date
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def api_call(base_url, path, method="GET", data=None):
    body = None if data is None else json.dumps(data).encode("utf-8")
    request = Request(
        base_url.rstrip("/") + path,
        data=body,
        method=method,
        headers={"Content-Type": "application/json"},
    )
    with urlopen(request, timeout=15) as response:
        return json.load(response)


def main():
    parser = argparse.ArgumentParser(description="Demonstrate Trent's nutrition features")
    parser.add_argument("--url", default="http://127.0.0.1:5000")
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--log-sample", action="store_true",
                        help="Add a sample meal, display it, then remove that meal")
    args = parser.parse_args()
    selected = date.fromisoformat(args.date)
    if selected.isoformat() != args.date or selected.year < 1000:
        parser.error("--date must use YYYY-MM-DD with a year of 1000 or later")

    meal_id = None
    try:
        foods = api_call(args.url, "/api/foods")
        print("Available foods:")
        print(json.dumps(foods, indent=2))

        if args.log_sample:
            by_name = {food["name"]: food["id"] for food in foods}
            if "Egg" not in by_name or "Oatmeal" not in by_name:
                raise ValueError("The sample requires Egg and Oatmeal from database/seed.sql")
            result = api_call(args.url, "/api/meals", "POST", {
                "meal_type": "Breakfast", "meal_date": args.date,
                "items": [{"food_id": by_name["Egg"], "servings": 2},
                          {"food_id": by_name["Oatmeal"], "servings": 1}],
            })
            meal_id = result["meal"]["id"]
            print(f"Created demonstration meal {meal_id}.")

        for endpoint in ("meals", "nutrition", "recommendations"):
            print(f"\n{endpoint.capitalize()} for {args.date}:")
            print(json.dumps(api_call(args.url, f"/api/{endpoint}?date={args.date}"), indent=2))
    finally:
        if meal_id is not None:
            try:
                api_call(args.url, f"/api/meals/{meal_id}", "DELETE")
                print(f"\nRemoved demonstration meal {meal_id}; existing meals were preserved.")
            except (HTTPError, URLError) as error:
                print(f"Cleanup failed for meal {meal_id}: {error}")
                print(f"Remove it using DELETE /api/meals/{meal_id} when the API is available.")
                raise


if __name__ == "__main__":
    try:
        main()
    except HTTPError as error:
        print(f"API error {error.code}: {error.read().decode('utf-8')}")
        raise SystemExit(1)
    except URLError:
        print("Could not reach the app. Start MySQL and run python -m backend.app first.")
        raise SystemExit(1)
    except ValueError as error:
        print(error)
        raise SystemExit(1)
