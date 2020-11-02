from restapi.customizer import BaseCustomizer
from restapi.models import fields, validate
from restapi.utilities.logs import log


class Customizer(BaseCustomizer):
    @staticmethod
    def custom_user_properties_pre(properties):
        extra_properties = {}
        # if 'myfield' in properties:
        #     extra_properties['myfield'] = properties['myfield']
        return properties, extra_properties

    @staticmethod
    def custom_user_properties_post(user, properties, extra_properties, db):

        try:
            group = db.Group.nodes.get(shortname="default")
        except db.Group.DoesNotExist:
            log.warning("Unable to find default group, creating")
            group = db.Group()
            group.fullname = "Default user group"
            group.shortname = "default"
            group.save()

        log.info("Link {} to group {}", user.email, group.shortname)
        user.belongs_to.connect(group)

        return True

    @staticmethod
    def manipulate_profile(ref, user, data):
        data["declared_institution"] = user.declared_institution

        return data

    @staticmethod
    def get_custom_input_fields(request, scope):

        # required = request and request.method == "POST"
        # It is defined for all scopes (ADMIN, PROFILE and REGISTRATION)
        if scope == BaseCustomizer.ADMIN:
            label = "Working institution"
        else:
            label = "Do you work at one of the following institutions:"
        return {
            "declared_institution": fields.Str(
                required=True,
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
    def get_custom_output_fields(request):
        fields = Customizer.get_custom_input_fields(request, scope=BaseCustomizer.ADMIN)

        return fields
