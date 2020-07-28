from restapi.models import AdvancedList, InputSchema, fields, validate


class Spatial(InputSchema):
    latitude = fields.Float(required=True, data_key="lat")
    longitude = fields.Float(required=True, data_key="long")


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
        missing="all", validate=validate.OneOf(["all", "video", "image"]),
    )
    provider = fields.Str(allow_none=True)
    city = fields.Str(allow_none=True)
    country = fields.Str(description="production country, codelist iso3166-1")
    # Default is True? Or False?
    missingDate = fields.Bool(missing=True)
    yearfrom = fields.Int(
        allow_none=True,
        description="production year range: start year of the range",
        validate=validate.Range(min=1890, max=2000),
    )
    yearto = fields.Int(
        allow_none=True,
        description="production year range: end year of the range",
        validate=validate.Range(min=1890, max=2000),
    )

    iprstatus = fields.Str(
        description="IPR status",
        allow_none=True,
        validate=validate.OneOf(
            # Should be extracted from codelist.RIGHTS_STATUS
            ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10"]
        ),
    )
    terms = fields.List(
        fields.Nested({"iri": fields.Str(), "label": fields.Str(required=True)})
    )

    # geo_distance = fields.Nested(GeoDistance)
    annotated_by = fields.Str(description="User's uuid")


class AnnotationSearchFilter(InputSchema):

    type = fields.Str(
        missing="all", validate=validate.OneOf(["all", "video", "image", "text"]),
    )
    provider = fields.Str(allow_none=True)
    # Sent by postman, not used in endpoint?
    country = fields.Str(description="production country, codelist iso3166-1")
    yearfrom = fields.Int(
        allow_none=True,
        description="production year range: start year of the range",
        validate=validate.Range(min=1890, max=2000),
    )
    yearto = fields.Int(
        allow_none=True,
        description="production year range: end year of the range",
        validate=validate.Range(min=1890, max=2000),
    )

    iprstatus = fields.Str(
        description="IPR status",
        allow_none=True,
        validate=validate.OneOf(
            # Should be extracted from codelist.RIGHTS_STATUS
            ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10"]
        ),
    )
    terms = fields.List(
        fields.Nested({"iri": fields.Str(), "label": fields.Str(required=True)})
    )

    geo_distance = fields.Nested(GeoDistance)


class SearchCriteria(InputSchema):
    match = fields.Nested(SearchMatch, required=True, allow_none=True)
    filtering = fields.Nested(SearchFilter, data_key="filter", required=True)


class AnnotationSearchCriteria(InputSchema):
    match = fields.Nested(SearchMatch, required=True)
    filtering = fields.Nested(AnnotationSearchFilter, data_key="filter", required=True)


class AnnotationSearch(InputSchema):
    annotation_type = fields.Str(
        data_key="type", required=True, validate=validate.OneOf(["TAG", "VIM", "TVS"])
    )
    geo_distance = fields.Nested(GeoDistance)
    creation = fields.Nested(AnnotationSearchCriteria)
