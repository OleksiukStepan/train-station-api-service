from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
)


crew_schema = extend_schema_view(
    list=extend_schema(
        description="Retrieve a list of crew members. "
                    "Allows ordering by `first_name` or `last_name`",
        parameters=[
            OpenApiParameter(
                name="ordering",
                type=OpenApiTypes.STR,
                description=(
                    "Specify fields to order the results by. "
                    "Available fields are `first_name` and `last_name`. "
                    "Prefix with `-` for descending order. "
                    "Multiple fields can be separated by commas "
                    "(ex. ?ordering=first_name or ?ordering=-last_name)"
                ),
            ),
        ],
    ),
)
