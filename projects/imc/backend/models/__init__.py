from restapi.models import AdvancedList, InputSchema, fields, validate


class Spatial(InputSchema):
    latitude = fields.Flot(required=True, data_key="lat")
    longitude = fields.Flot(required=True, data_key="long")


class GeoDistance(InputSchema):
    distance = fields.Int(
        required=True, description="Distance in km", validate=validate.Range(min=1)
    )
    location = fields.Nested(Spatial, required=True, description="Pin location")


class SearchMatch(InputSchema):
    term = fields.Str(required=True)
    fields = AdvancedList(
        fields.Str(
            validate=validate.OneOf(["title", "contributor", "keyword", "description"])
        ),
        required=True,
        min_items=1,
    )


class SearchFilter(InputSchema):

    type = fields.Str(
        missing="all",
        # Text is only used in annotations_search?
        validate=validate.OneOf(["all", "video", "image", "text"]),
    )
    provider = fields.Str()
    country = fields.Str(description="production country, codelist iso3166-1")
    yearfrom = fields.Int(
        description="production year range, start year of the range",
        validate=validate.Range(min=1900, max=2000),
    )
    yearto = fields.Int(
        description="production year range, end year of the range, maximum=2000, yearto>=yearfrom",
        validate=validate.Range(min=1900, max=2000),
    )

    iprstatus = fields.Str(
        description="IPR status",
        validate=validate.OneOf(
            ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10"]
        ),
    )
    terms = fields.List(
        fields.Nested({"iri": fields.Str(), "label": fields.Str(required=True)})
    )

    geo_distance = fields.Nested(GeoDistance)
    annotated_by = fields.Dtr(description="User's uuid")


class AnnotationSearchCriteria(InputSchema):
    annotation_type = fields.Str(
        data_key="type", required=True, validate=validate.OneOf(["TAG", "VIM", "TVS"])
    )
    geo_distance = fields.Nested(GeoDistance)
    creation = fields.Nested(
        {"match": fields.Nested(SearchMatch), "filter": fields.Nested(SearchFilter)}
    )
