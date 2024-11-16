from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
)


ticket_schema = extend_schema_view(
    list=extend_schema(
        description="Retrieve a list of tickets. "
                    "Allows filtering by various fields, "
                    "and ordering by `cargo`, `seat`, or `journey`",
        parameters=[
            OpenApiParameter(
                name="ordering",
                type=OpenApiTypes.STR,
                description=(
                    "Specify fields to order the results by. "
                    "Available fields are `cargo`, `seat`, and `journey`. "
                    "Prefix with `-` for descending order. "
                    "Multiple fields can be separated by commas "
                    "(ex. ?ordering=cargo or ?ordering=-seat)."
                ),
            ),
        ],
    ),
)
