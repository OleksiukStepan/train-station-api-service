from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
)


train_schema = extend_schema_view(
    list=extend_schema(
        description="Retrieve a list of trains. "
                    "Allows filtering trains by `train_name` and `train_type`",
        parameters=[
            OpenApiParameter(
                name="train_name",
                type=OpenApiTypes.STR,
                description="Filter trains by train name. "
                            "(ex. ?train_name=Express)",
            ),
            OpenApiParameter(
                name="train_type",
                type=OpenApiTypes.STR,
                description="Filter trains by train type ID(s). "
                            "(ex. ?train_type=1,2,3)",
            ),
            OpenApiParameter(
                name="ordering",
                type=OpenApiTypes.STR,
                description=(
                    "Specify fields to order the results by. "
                    "Available fields are `name`, `cargo_num`, "
                    "`places_in_cargo`, and `train_type`. "
                    "Prefix with `-` for descending order. "
                    "Multiple fields can be separated by commas "
                    "(ex. ?ordering=name or ?ordering=-cargo_num)"
                ),
            ),
        ],
    ),
)
