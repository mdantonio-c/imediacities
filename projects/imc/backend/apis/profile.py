from marshmallow import fields, validate


class CustomProfile:
    def __init__(self):
        pass

    @staticmethod
    def manipulate(ref, user, data):
        data['declared_institution'] = user.declared_institution

        return data

    # strip_required is True when the model is invoked by put endpoints
    @staticmethod
    def get_custom_fields(strip_required=False):
        return {
            'declared_institution': fields.Str(
                required=False,
                default="none",
                validate=validate.OneOf(
                    choices=['archive', 'university', 'research_institution', 'none'],
                    labels=[
                        'Archive',
                        'University',
                        'Research Institution',
                        'None of the above',
                    ],
                ),
            )
        }
