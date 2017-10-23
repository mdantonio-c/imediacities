
from utilities.logs import get_logger
from restapi.services.neo4j.graph_endpoints import graph_transactions

from imc.models.neo4j import (
    Annotation, TVSBody, VIMBody,
    VideoSegment, Shot, ResourceBody, TextualBody, Item
)

log = get_logger(__name__)


class AnnotationRepository():
    """ """

    def __init__(self, graph):
        self.graph = graph

    # @graph_transactions
    def create_tag_annotation(self, user, body, target, selector):
        log.debug("Create a new manual annotation")

        # create annotation node
        anno = Annotation(annotation_type='TAG').save()
        if user is not None:
            # add creator
            anno.creator.connect(user)

        if isinstance(target, Item):
            anno.source_item.connect(target)
        elif isinstance(target, Annotation):
            anno.source_item.connect(target.source_item.single())
        elif isinstance(target, Shot):
            anno.source_item.connect(target.item.single())

        if selector is not None:
            s_start, s_end = selector['value'].lstrip('t=').split(',')
            log.debug('start:{}, end:{}'.format(s_start, s_end))
            # search for existing segment
            segment = self.graph.VideoSegment.nodes.get_or_none(
                start_frame_idx=s_start, end_frame_idx=s_end)
            log.debug('Segment does exist? {}'.format(
                True if segment else False))
            if segment is None:
                segment = VideoSegment(
                    start_frame_idx=s_start, end_frame_idx=s_end).save()
            anno.targets.connect(segment)
        else:
            anno.targets.connect(target)
        # add body
        if body['type'] == 'ResourceBody':
            source = body['source']
            iri = source if isinstance(source, str) \
                else source.get('iri')
            log.debug('ResourceBody with IRI:{}'.format(iri))
            # look for existing Resource
            # do not update the existing resource
            bodyNode = self.graph.ResourceBody.nodes.get_or_none(iri=iri)
            if bodyNode is None:
                bodyNode = ResourceBody(iri=iri)
                if not isinstance(source, str):
                    bodyNode.name = source.get('name')
                if 'spatial' in body:
                    coord = [body['spatial']['lat'], body['spatial']['long']]
                    log.debug('lat: {}, long:{}'.format(coord[0], coord[1]))
                    bodyNode.spatial = coord
                bodyNode.save()
        elif body['type'] == 'TextualBody':
            bodyNode = TextualBody(
                value=body['value'], language=body['language']).save()
        else:
            # should never be reached
            raise ValueError('Invalid body: {}'.format(body['type']))
        anno.bodies.connect(bodyNode)
        return anno

    def delete_manual_annotation(self, anno):
        body = anno.bodies.single()
        if body:
            original_body = body.downcast()
            log.debug('body instance of {}'.format(original_body.__class__))
            # at moment never remove a ResourceBody
            if isinstance(original_body, TextualBody):
                original_body.delete()
        # delete any orphan video segments (NOT SHOT!)
        targets = anno.targets.all()
        for t in targets:
            target_labels = t.labels()
            log.debug("Target label(s): {}".format(target_labels))
            if 'VideoSegment' in target_labels and \
                    'Shot' not in target_labels and \
                    self.is_orphan_segment(t.downcast(target_class='VideoSegment')):
                t.delete()
                log.debug('Deleted orphan segment')
        anno.delete()
        log.debug('Manual annotation with ID:{} successfully deleted'
                  .format(anno.uuid))

    @staticmethod
    def is_orphan_segment(node):
        return False if len(node.annotation.all()) > 1 else True

    @graph_transactions
    def create_tvs_annotation(self, item, shots):
        if not shots:
            raise ValueError('List of shots cannot be empty')
        # create annotation node
        annotation = Annotation(generator='FHG', annotation_type='TVS').save()
        # add target
        annotation.targets.connect(item)
        annotation.source_item.connect(item)

        # add body
        tvs_body = TVSBody().save()
        annotation.bodies.connect(tvs_body)

        # foreach shot create a node and connect it properly
        for shot in shots:
            shot.save()
            tvs_body.segments.connect(shot)
            item.shots.connect(shot)

    @graph_transactions
    def delete_tvs_annotation(self, annotation):
        log.info('Delete existing TVS annotation')
        tvs_body = annotation.bodies.single()
        if tvs_body:
            original_tvs_body = tvs_body.downcast()
            log.info(original_tvs_body.__class__)
            for segment in original_tvs_body.segments:
                segment.delete()
            original_tvs_body.delete()
        annotation.delete()

    @graph_transactions
    def create_vim_annotation(self, item, estimates):
        if not estimates or len(estimates) == 0:
            raise ValueError('List of video motion estimates cannot be empty')
        for q in estimates:
            # get video shot by shot number
            shot = None
            try:
                shot = item.shots.search(shot_num=q[0])[0]
            except BaseException:
                log.warning("Cannot find shot number {0}. "
                            "VIM Annotation *NOT* created.".format(q[0]))
                continue

            # create annotation node
            annotation = Annotation(
                generator='FHG', annotation_type='VIM').save()
            # add target
            annotation.targets.connect(shot)
            annotation.source_item.connect(item)
            # add body
            vim_body = VIMBody()
            motions_dict = q[1]
            log.debug('--------------------------------')
            log.debug(motions_dict)
            log.debug('--------------------------------')
            vim_body.no_motion = motions_dict['NoMotion']
            vim_body.left_motion = motions_dict['LeftMotion']
            vim_body.right_motion = motions_dict['RightMotion']
            vim_body.up_motion = motions_dict['UpMotion']
            vim_body.down_motion = motions_dict['DownMotion']
            vim_body.zoom_in_motion = motions_dict['ZoomInMotion']
            vim_body.zoom_out_motion = motions_dict['ZoomOutMotion']
            vim_body.roll_cw_motion = motions_dict['RollCWMotion']
            vim_body.roll_ccw_motion = motions_dict['RollCCWMotion']
            vim_body.x_shake = motions_dict['XShake']
            vim_body.y_shake = motions_dict['YShake']
            vim_body.roll_shake = motions_dict['RollShake']
            vim_body.camera_shake = motions_dict['CameraShake']
            vim_body.inner_rhythm_fluid = motions_dict['InnerRhythmFluid']
            vim_body.inner_rhythm_staccato = motions_dict['InnerRhythmStaccato']
            vim_body.inner_rhythm_no_motion = motions_dict['InnerRhythmNoMotion']
            vim_body.save()
            annotation.bodies.connect(vim_body)

    @graph_transactions
    def delete_vim_annotation(self, annotation):
        log.debug('Delete existing VIM annotation')
        vim_body = annotation.bodies.single()
        if vim_body:
            original_vim_body = vim_body.downcast()
            log.info(original_vim_body.__class__)
            original_vim_body.delete()
        annotation.delete()
