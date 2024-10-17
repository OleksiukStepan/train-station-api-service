from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
)


train_type_schema = extend_schema_view(
    list=extend_schema(
        description="Retrieve a list of train types. "
                    "Allows ordering by `name`.",
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
