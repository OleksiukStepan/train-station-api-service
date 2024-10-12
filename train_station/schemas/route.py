from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema, OpenApiParameter,
)


route_schema = extend_schema_view(
    list=extend_schema(
        description="Retrieve a list of routes. "
                    "Allows filter routes by `source` and `destination` names",
        parameters=[
            OpenApiParameter(
                name="source",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filter routes by the source station name",
                required=False,
            ),
            OpenApiParameter(
                name="destination",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filter routes by the destination station name",
                required=False,
            ),
        ],
    ),
)
