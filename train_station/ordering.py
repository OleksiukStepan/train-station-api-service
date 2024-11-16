from rest_framework.request import Request


class OrderingHelper:
    ordering_param = "ordering"
    default_param = "-pk"

    field_mapping = {
        "train": "train__name",
        "route": "route__source__name",
    }

    @classmethod
    def get_ordering_fields(
        cls, request: Request, fields: list[str]
    ) -> list[str]:
        ordering = request.query_params.get(
            cls.ordering_param,
            cls.default_param
        )
        ordering_fields = ordering.split(",")
        all_fields = set(["-" + field for field in fields] + fields)
        processed_ordering_fields = [
            cls.field_mapping.get(field.lstrip("-"), field)
            if field in all_fields else None
            for field in ordering_fields
        ]

        processed_ordering_fields = [
            field for field in processed_ordering_fields if field
        ]

        if not processed_ordering_fields:
            return [cls.default_param]

        return processed_ordering_fields
