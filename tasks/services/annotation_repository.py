
from rapydo.utils.logs import get_logger
from neomodel import db

from imc.models.neo4j import (
    Annotation, TVSBody
)

log = get_logger(__name__)


class AnnotationRepository():
    """ """

    def __init__(self, graph):
        self.graph = graph

    @db.transaction
    def create_tvs_annotation(self, item, shots):
        if not shots:
            raise ValueError('List of shots cannot be empty')
        # create annotation node
        annotation = Annotation(generator='FHG', annotation_type='TVS').save()
        # add target
        annotation.targets.connect(item)
        annotation.source.connect(item)

        # add body
        tvs_body = TVSBody().save()
        annotation.bodies.connect(tvs_body)

        # foreach shot create a node and connect it properly
        for shot in shots:
            shot.save()
            tvs_body.segments.connect(shot)
            item.shots.connect(shot)

    @db.transaction
    def delete_tvs_annotation(self, annotation):
        # item = annotation.targets[0]
        # annotation.source.disconnect(item)
        # annotation.targets.disconnect(item)

        tvs_body = annotation.bodies[0]
        if tvs_body:
            for segment in tvs_body.segments:
                segment.delete()
            tvs_body.delete()
        annotation.delete()
