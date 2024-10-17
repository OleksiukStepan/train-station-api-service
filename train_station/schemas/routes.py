from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
)


route_schema = extend_schema_view(
    list=extend_schema(
        description="Retrieve a list of routes. "
                    "Allows filter routes by `source` and `destination` names",
        parameters=[
            OpenApiParameter(
                name="source",
                type=OpenApiTypes.STR,
                description="Filter routes by the source station name"
                            "(ex. ?source=Lviv)",
            ),
            OpenApiParameter(
                name="destination",
                type=OpenApiTypes.STR,
                description="Filter routes by the destination station name"
                            "(ex. ?destination=Kharkiv)",
            ),
            OpenApiParameter(
                name="ordering",
                type=OpenApiTypes.STR,
                description=(
                    "Specify fields to order the results by. "
                    "Available fields are `source`, `destination`, "
                    "and `distance`. Prefix with `-` for descending order. "
                    "Multiple fields can be separated by commas "
                    "(ex. ?ordering=source or ?ordering=-distance)"
                ),
            )
        ],
    ),
)
