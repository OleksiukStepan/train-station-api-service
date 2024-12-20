from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
)


order_schema = extend_schema_view(
    list=extend_schema(
        description="Retrieve a list of orders."
                    "Allows filter orders by `created_at` date (YYYY-MM-DD)",
        parameters=[
            OpenApiParameter(
                name="created_at",
                type=OpenApiTypes.STR,
                description="Filter orders by creation date. "
                            "(ex. ?title=2024-10-09)",
            ),
            OpenApiParameter(
                name="ordering",
                type=OpenApiTypes.STR,
                description=(
                    "Specify fields to order the results by. "
                    "Available field is `created_at`. "
                    "Prefix with `-` for descending order "
                    "(ex. ?ordering=created_at or ?ordering=-created_at)"
                ),
            )
        ],
    ),
)
