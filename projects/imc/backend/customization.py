from typing import Any, Tuple

from restapi.customizer import BaseCustomizer, FlaskRequest, Props, User
from restapi.models import fields, validate
from restapi.rest.definition import EndpointResource


class Customizer(BaseCustomizer):
    @staticmethod
    def custom_user_properties_pre(
        properties: Props,
    ) -> Tuple[Props, Props]:
        extra_properties = {}
        # if 'myfield' in properties:
        #     extra_properties['myfield'] = properties['myfield']
        return properties, extra_properties

    @staticmethod
    def custom_user_properties_post(
        user: User, properties: Props, extra_properties: Props, db: Any
    ) -> None:
        pass

    @staticmethod
    def manipulate_profile(ref: EndpointResource, user: User, data: Props) -> Props:
        data["declared_institution"] = user.declared_institution

        return data

    @staticmethod
    def get_custom_input_fields(request: FlaskRequest, scope: int) -> Props:

        required = request and request.method == "POST"
        # It is defined for all scopes (ADMIN, PROFILE and REGISTRATION)
        if scope == BaseCustomizer.ADMIN:
            label = "Working institution"
        else:
            label = "Do you work at one of the following institutions:"
        return {
            "declared_institution": fields.Str(
                required=required,
                description="",
                label=label,
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

    @staticmethod
    def get_custom_output_fields(request: FlaskRequest) -> Props:
        fields = Customizer.get_custom_input_fields(request, scope=BaseCustomizer.ADMIN)

        return fields
