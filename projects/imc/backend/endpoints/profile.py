from restapi.models import fields, validate


class CustomProfile:
    def __init__(self):
        pass

    @staticmethod
    def manipulate(ref, user, data):
        data["declared_institution"] = user.declared_institution

        return data

    @staticmethod
    def get_user_editable_fields(request):
        return {}

    @staticmethod
    def get_custom_fields(request):

        # required = request and request.method == "POST"
        return {
            "declared_institution": fields.Str(
                required=False,
                default="none",
                validate=validate.OneOf(
                    choices=["archive", "university", "research_institution", "none"],
                    labels=[
                        "Archive",
                        "University",
                        "Research Institution",
                        "None of the above",
                    ],
                ),
            )
        }
