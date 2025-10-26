import json
import jsonschema
from jsonschema import ValidationError


def validate_report_schema(report: object) -> bool:
    try:
        with open("report_schema.json") as f:
            schema = json.load(f)
        jsonschema.validate(instance=report, schema=schema)
        print("Report is valid according to schema.")
        return True
    except ValidationError as e:
        print(f"Schema validation failed: {e.message}")
        return False
    except Exception as e:
        print(f"Unexpected validation error: {e}")
        return False
