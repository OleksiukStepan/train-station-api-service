from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
)

station_schema = extend_schema_view(
    list=extend_schema(
        description="Retrieve a list of stations. "
                    "Allows ordering by `name`",
        parameters=[
            OpenApiParameter(
                name="ordering",
                type=OpenApiTypes.STR,
                description=(
                    "Specify fields to order the results by. "
                    "Available field is `name`. "
                    "Prefix with `-` for descending order "
                    "(ex. ?ordering=name or ?ordering=-name)"
                ),
            ),
        ],
    ),
)
