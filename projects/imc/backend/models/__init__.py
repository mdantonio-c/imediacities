from marshmallow import ValidationError, pre_load
from restapi.models import PartialSchema, Schema, fields, validate

allowed_term_fields = ("title", "description", "keyword", "contributor")
allowed_anno_types = ("TAG", "DSC", "LNK")
allowed_item_types = ("all", "video", "image")


class Spatial(Schema):
    latitude = fields.Float(required=True, data_key="lat")
    longitude = fields.Float(required=True, data_key="long")


class GeoDistance(Schema):
    distance = fields.Int(
        required=True, description="Distance in km", validate=validate.Range(min=1)
    )
    location = fields.Nested(Spatial, required=True, description="Pin location")


class SearchMatch(Schema):
    term = fields.Str(required=True)
    fields = fields.List(  # type: ignore
        fields.Str(validate=validate.OneOf(allowed_term_fields)),
        required=True,
        min_items=1,
    )


class AnnotatedByCriteria(Schema):
    user = fields.Str(required=True, description="User's uuid")
    type = fields.Str(
        missing="TAG",
        validate=validate.OneOf(allowed_anno_types),
    )


class SearchFilter(Schema):

    type = fields.Str(
        missing="all",
        validate=validate.OneOf(allowed_item_types),
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
    annotated_by = fields.Nested(AnnotatedByCriteria, allow_none=True)


class AnnotationSearchCriteria(Schema):
    match = fields.Nested(SearchMatch, allow_none=True)
    filtering = fields.Nested(SearchFilter, data_key="filter", required=True)


# used by POST /search
class SearchCriteria(PartialSchema):
    match = fields.Nested(SearchMatch, required=True, allow_none=True)
    filtering = fields.Nested(SearchFilter, data_key="filter", required=True)


# used by POST /bulk
class BulkImportSchema(Schema):
    guid = fields.UUID(required=True)
    mode = fields.Str(missing="skip")
    update = fields.Bool(missing=False)
    retry = fields.Bool(missing=False)


class BulkUpdateSchema(Schema):
    guid = fields.UUID(required=True)
    force_reprocessing = fields.Bool(missing=False)


class BulkV2Schema(Schema):
    guid = fields.UUID(required=True)
    retry = fields.Bool(missing=False)


class BulkDeleteSchema(Schema):
    @pre_load
    def set_uuids(self, data, **kwargs):
        if not data.get("delete_all") and "uuids" not in data:
            raise ValidationError("Please specify either a list of uuids or delete_all")
        return data

    entity = fields.Str(
        required=True, validate=validate.OneOf(["AVEntity", "NonAVEntity"])
    )
    uuids = fields.List(fields.UUID(), min_items=1)
    delete_all = fields.Bool(missing=False)


class BulkSchema(Schema):
    @pre_load
    def init_action(self, data, **kwargs):

        if not data:
            raise ValidationError(
                "Missing action: expected one of update, import, delete, v2"
            )

        return data

    update = fields.Nested(BulkUpdateSchema)
    import_ = fields.Nested(BulkImportSchema, data_key="import")
    v2 = fields.Nested(BulkV2Schema)
    delete = fields.Nested(BulkDeleteSchema)


# used by POST /annotations/search
class AnnotationSearch(Schema):
    annotation_type = fields.Str(
        data_key="type", required=True, validate=validate.OneOf(["TAG", "VIM", "TVS"])
    )
    geo_distance = fields.Nested(GeoDistance)
    creation = fields.Nested(AnnotationSearchCriteria)


# used by PATCH /annotations/<anno_id>
class PatchDocument(Schema):

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
class Target(Schema):
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
class SearchPlaceParameters(Schema):
    place_list = fields.List(
        fields.Nested(
            {
                "creation-id": fields.Str(required=True),
                "place-ids": fields.List(fields.Str(), required=True, min_items=1),
            },
        ),
        description="Criteria for the search",
        required=True,
        data_key="relevant-list",
        min_items=1,
    )


# Rapresent the scene cut that is the first frame of the shot.
# For homogeneity, the first zero cut must also be provided.
class SceneCut(Schema):

    shot_num = fields.Int(required=True, validate=validate.Range(min=0))
    cut = fields.Int(required=True, validate=validate.Range(min=0))
    confirmed = fields.Bool(missing=False)
    double_check = fields.Bool(missing=False)
    annotations = fields.List(
        fields.Str(), required=True, unique=True, description="Annotation's uuid"
    )


# used by POST /videos/<video_id>/shot-revision
class ShotRevision(Schema):
    shots = fields.List(
        fields.Nested(SceneCut),
        required=True,
        min_items=1,
        description="The new list of scene cuts",
    )
    exitRevision = fields.Bool(missing=True)
