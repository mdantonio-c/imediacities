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
    # country = fields.Str(description="production country, codelist iso3166-1")
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


class AnnotationSearchCriteria(InputSchema):
    match = fields.Nested(SearchMatch, required=True)
    filtering = fields.Nested(AnnotationSearchFilter, data_key="filter", required=True)


# used by POST /search
class SearchCriteria(InputSchema):
    match = fields.Nested(SearchMatch, required=True, allow_none=True)
    filtering = fields.Nested(SearchFilter, data_key="filter", required=True)


# used by POST /annotations/search
class AnnotationSearch(InputSchema):
    annotation_type = fields.Str(
        data_key="type", required=True, validate=validate.OneOf(["TAG", "VIM", "TVS"])
    )
    geo_distance = fields.Nested(GeoDistance)
    creation = fields.Nested(AnnotationSearchCriteria)


# used by PATCH /annotations/<anno_id>
class PatchDocument(InputSchema):

    patch_op = fields.Str(
        required=True,
        data_key="op",
        description="The operation to be performed",
        # validate=validate.OneOf(["add", "remove", "replace", "move", "copy", "test"])
        validate=validate.OneOf(["add", "remove"]),
    )
    path = fields.Str(
        required=True,
        description="A JSON-Pointer",
        # Invalid path to patch segmentation
        validate=validate.OneOf(["/bodies/0/segments"]),
    )

    value = fields.Str(
        required=True, description="The value to be used within the operations"
    )


# used by POST /lists/<list_id>/items
class Target(InputSchema):
    target = fields.Nested(
        {
            "id": fields.Str(required=True),
            "type": fields.Str(
                required=True, validate=validate.OneOf(["item", "shot"])
            ),
        },
        required=True,
    )


# used by POST /search_place
class SearchPlaceParameters(InputSchema):
    place_list = AdvancedList(
        fields.Nested(
            {
                "creation-id": fields.Str(required=True),
                "place-ids": AdvancedList(fields.Str(), required=True, min_items=1),
            },
        ),
        description="Criteria for the search",
        required=True,
        data_key="relevant-list",
        min_items=1,
    )


# Rapresent the scene cut that is the first frame of the shot.
# For homogeneity, the first zero cut must also be provided.
class SceneCut(InputSchema):

    shot_num = fields.Int(required=True, validate=validate.Range(min=0))
    cut = fields.Int(required=True, validate=validate.Range(min=0))
    confirmed = fields.Bool(missing=False)
    double_check = fields.Bool(missing=False)
    annotations = AdvancedList(
        fields.Str(), required=True, unique=True, description="Annotation's uuid"
    )


# used by POST /videos/<video_id>/shot-revision
class ShotRevision(InputSchema):
    shots = AdvancedList(
        fields.Nested(SceneCut),
        required=True,
        min_items=1,
        description="The new list of scene cuts",
    )
    exitRevision = fields.Bool(missing=True)
