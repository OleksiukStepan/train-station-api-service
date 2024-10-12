from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
)


train_schema = extend_schema_view(
    list=extend_schema(
        description="Retrieve a list of trains. "
                    "Allows filtering trains by `train_type`",
        parameters=[
            OpenApiParameter(
                name="train_type",
                type=OpenApiTypes.STR,
                description="Filter trains by train type ID(s). "
                            "(ex. ?train_type=1,2,3)",
            ),
        ],
    ),
)
