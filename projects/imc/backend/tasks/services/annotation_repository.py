
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
    def create_tag_annotations(self, user, bodies, target, selector):
        # deduplicate body annotations
        warnings, bodies = self.deduplicate_tags(bodies, target, selector)
        if len(warnings) > 0:
            for msg in warnings:
                log.warning(msg)
        if len(bodies) == 0:
            raise DuplicatedAnnotationError(
                "Annotation cannot be created.", warnings)

        log.debug("Create new tag annotations")
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
        # add bodies
        for body in bodies:
            if body['type'] == 'ResourceBody':
                source = body['source']
                iri = source if isinstance(source, str) \
                    else source.get('iri')
                log.debug('ResourceBody with IRI:{}'.format(iri))
                # look for existing Resource
                # do not update the existing resource
                bodyNode = self.graph.ResourceBody.nodes.get_or_none(iri=iri)
                if bodyNode is None:
                    log.debug('new ResourceBody')
                    bodyNode = ResourceBody(iri=iri)
                    if not isinstance(source, str):
                        bodyNode.name = source.get('name')
                    if 'spatial' in body:
                        coord = [body['spatial']['lat'],
                                 body['spatial']['long']]
                        log.debug('lat: {}, long:{}'.format(
                            coord[0], coord[1]))
                        bodyNode.spatial = coord
                    bodyNode.save()
            elif body['type'] == 'TextualBody':
                text_lang = body.get('language', 'en')
                bodyNode = TextualBody(
                    value=body['value'], language=text_lang).save()
                bodyNode.save()
            else:
                # should never be reached
                raise ValueError('Invalid body: {}'.format(body['type']))
            anno.bodies.connect(bodyNode)
        return anno

    def delete_manual_annotation(self, anno, btype, bid):
        '''
        b_type and b_id can be used to delete only a single body in the
        annotation if multiple bodies exist.
        '''
        log.debug('Deleting annotation ID:{anno_id} with body reference [{btype}:{bid}]'.format(
            anno_id=anno.uuid, btype=btype, bid=bid))
        bodies = anno.bodies.all()
        body_list_size_before = len(bodies)
        log.debug('body list size before deletion: {}'.format(
            body_list_size_before))
        single_body = True if btype is not None and bid is not None else False
        log.debug('Deleting single body?: {}'.format(single_body))
        body_found = False
        for body in bodies:
            original_body = body.downcast()
            log.debug('body instance of {}'.format(original_body.__class__))
            if single_body:
                # ONLY the referenced body
                if isinstance(original_body, ResourceBody) and btype == 'resource':
                    if bid == original_body.iri:
                        # disconnect that node
                        body_found = True
                        anno.bodies.disconnect(body)
                elif isinstance(original_body, TextualBody) and btype == 'textual':
                    if bid == original_body.value:
                        # remove the textual node
                        body_found = True
                        original_body.delete()
                if body_found:
                    break
            else:
                if isinstance(original_body, ResourceBody):
                    # never remove a ResourceBody
                    anno.bodies.disconnect(body)
                else:
                    original_body.delete()
        # refresh the list of bodies
        bodies = anno.bodies.all()
        body_list_size_after = len(bodies)
        log.debug('body list size after deletion: {}'.format(
            body_list_size_after))
        if single_body and not body_found:
            raise ReferenceError("Annotation ID:{anno_id} cannot be deleted."
                                 " No body found for {btype}:{bid}".format(
                                     anno_id=anno.uuid, btype=btype, bid=bid))
        if body_list_size_after == 0:
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
            single_body_removed = ''
            if single_body:
                single_body_removed = ' Body {body_type}:{body_id}'.format(
                    body_type=btype, body_id=bid)
            log.info('Annotation with ID:{anno_id} successfully deleted.{msg}'.format(
                anno_id=anno.uuid, msg=single_body_removed))
        else:
            log.info('Annotation with ID:{anno_id}. ONLY body {body_type}:{body_id} removed'.format(
                anno_id=anno.uuid, body_type=btype, body_id=bid))

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

    def deduplicate_tags(self, bodies, target, selector):
        ''' Check for esisting bodies for the given target. If all bodies
        already exist, throw a duplication exception exception. If the
        annotation contains some duplicates, report them as warnings.
        '''
        warnings = []
        filtered_bodies = []
        for body in bodies:
            if body['type'] != 'ResourceBody':
                filtered_bodies.append(body)
                continue
            if selector is not None:
                # TODO manage deduplication with selector
                filtered_bodies.append(body)
                continue
            source = body['source']
            iri = source if isinstance(source, str) else source.get('iri')
            query = "MATCH (a:Annotation) WHERE a.annotation_type='TAG' " \
                "match (a)-[:HAS_TARGET]-(t:AnnotationTarget) where t.uuid='{target_uuid}' " \
                "match (a)-[:HAS_BODY]->(b:ResourceBody) where b.iri='{body_iri}' " \
                "return count(b)"
            results = self.graph.cypher(query.format(
                target_uuid=target.uuid, body_iri=iri))
            count = [row[0] for row in results][0]
            log.debug("Duplicated found: {0}".format(count))
            if count > 0:
                warnings.append("Duplicated tag: '{name}' - '{iri}'".format(
                    name=source.get('name', ''), iri=iri))
                continue
            filtered_bodies.append(body)
        log.debug("Filtered bodies: {0}".format(filtered_bodies))
        return warnings, filtered_bodies


class DuplicatedAnnotationError(Exception):
    pass
