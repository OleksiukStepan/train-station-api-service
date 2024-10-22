from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
)


journey_schema = extend_schema_view(
    list=extend_schema(
        description="Retrieve a list of journeys. "
                    "Allows filtering by `departure_time`, `arrival_time`, "
                    "`source`, and `destination`",
        parameters=[
            OpenApiParameter(
                name="departure_time",
                type=OpenApiTypes.STR,
                description="Filter journeys by the departure date "
                            "(ex. ?departure_time=2024-10-10)",
            ),
            OpenApiParameter(
                name="arrival_time",
                type=OpenApiTypes.STR,
                description="Filter journeys by the arrival date "
                            "(ex. ?arrival_time=2024-10-12)",
            ),
            OpenApiParameter(
                name="source",
                type=OpenApiTypes.STR,
                description="Filter journeys by the source station name "
                            "(ex. ?source=Lviv)",
            ),
            OpenApiParameter(
                name="destination",
                type=OpenApiTypes.STR,
                description="Filter journeys by the destination station name"
                            "(ex. ?destination=Kharkiv)",
            ),
            OpenApiParameter(
                name="ordering",
                type=OpenApiTypes.STR,
                description=(
                    "Specify fields to order the results by. "
                    "Available fields are `route`, `train`, "
                    "`departure_time`, and `arrival_time`. "
                    "Prefix with `-` for descending order. "
                    "Multiple fields can be separated by commas. "
                    "(ex. ?ordering=departure_time or ?ordering=-arrival_time)"
                ),
            ),
        ],
    ),
)
