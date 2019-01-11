# -*- coding: utf-8 -*-

from datetime import datetime
import pytz
import json
from utilities.logs import get_logger
from restapi.services.neo4j.graph_endpoints import graph_transactions
from neomodel.cardinality import CardinalityViolation

from imc.models.neo4j import (
    Annotation, TVSBody, VIMBody, BibliographicReference,
    VideoSegment, Shot, ResourceBody, TextualBody, Item
)

log = get_logger(__name__)


class AnnotationRepository():
    """ """

    def __init__(self, graph):
        self.graph = graph

    # @graph_transactions
    def create_tag_annotation(self, user, bodies, target, selector,
                              is_private=False, embargo_date=None, automatic=False):
        # deduplicate body annotations
        warnings, bodies = self.deduplicate_tags(bodies, target, selector)
        if len(warnings) > 0:
            for msg in warnings:
                log.warning(msg)
        if len(bodies) == 0:
            raise ValueError("Annotation cannot be created.", warnings)
        if not automatic and user is None:
            raise ValueError("Annotation cannot be created.",
                             ["Missing creator for manual annotation"])

        log.debug("Creating a new tag annotation")
        # create annotation node
        anno = Annotation(annotation_type='TAG')
        if automatic:
            # at the moment ONLY FHG tools allowed
            anno.generator = 'FHG'
        anno.save()
        if not automatic:
            # add creator
            anno.creator.connect(user)

        if isinstance(target, Item):
            anno.source_item.connect(target)
        elif isinstance(target, Annotation):
            anno.source_item.connect(target.source_item.single())
        elif isinstance(target, Shot):
            anno.source_item.connect(target.item.single())
        else:
            raise ValueError("Invalid Target instance.")

        # target to a segment only for videos with a provided selector
        if selector is not None and isinstance(target, Item) and target.item_type == 'Video':
            if not isinstance(target, Item):
                raise ValueError('Selector allowed only for Item target.')
            s_start, s_end = map(
                int, selector['value'].lstrip('t=').split(','))
            log.debug('start:{}, end:{}'.format(s_start, s_end))
            # search for existing segment for the given item
            segment = self.lookup_existing_segment(s_start, s_end, target)
            log.debug('Segment does exist? {}'.format(
                True if segment else False))
            if segment is None:
                segment = VideoSegment(
                    start_frame_idx=s_start, end_frame_idx=s_end).save()
                # look up the shot where the segment is enclosed
                shots = self.get_enclosing_shots(segment, target)
                if shots is None or len(shots) == 0:
                    raise ValueError('Invalid state: cannot be found shot(s) enclosing '
                                     'selected segment [{0}]'.format(selector['value']))
                for shot in shots:
                    segment.within_shots.connect(shot)
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
                    log.debug('new ResourceBody for concept: {}'.format(source))
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
                text_lang = body.get('language')
                bodyNode = TextualBody(
                    value=body['value'], language=text_lang).save()
                bodyNode.save()
            elif body['type'] == 'ODBody':
                properties = {
                    'object_id': body['object_id'],
                    'confidence': body['confidence']
                }
                bodyNode = self.graph.ODBody(**properties).save()
                if 'region_sequence' in body:
                    sequence = json.dumps(body['region_sequence'])
                    fragment_selection = self.graph.AreaSequenceSelector(
                        sequence=sequence).save()
                    anno.refined_selection.connect(fragment_selection)
                # connect the concept
                concept = body['concept']['source']
                conceptNode = self.graph.ResourceBody.nodes.get_or_none(
                    iri=concept['iri'])
                if conceptNode is None:
                    log.debug(
                        'new ResourceBody for concept: {}'.format(concept))
                    conceptNode = ResourceBody(
                        iri=concept['iri'], name=concept['name']).save()
                bodyNode.object_type.connect(conceptNode)
            else:
                # should never be reached
                raise ValueError('Invalid body: {}'.format(body['type']))
            anno.bodies.connect(bodyNode)
        return anno

    def create_dsc_annotation(self, user, bodies, target, selector,
                              is_private=False, embargo_date=None):
        '''
        Create a "description" annotation used for private and public notes.
        '''
        visibility = 'private' if is_private else 'public'
        log.debug("Create a new {} description annotation".format(visibility))
        # create annotation node
        anno = Annotation(annotation_type='DSC', private=is_private).save()
        if embargo_date is not None:
            anno.embargo = embargo_date
            anno.save()
        # should we allow to create anno without a user of the system?
        if user is not None:
            anno.creator.connect(user)

        if isinstance(target, Item):
            anno.source_item.connect(target)
        elif isinstance(target, Annotation):
            anno.source_item.connect(target.source_item.single())
        elif isinstance(target, Shot):
            anno.source_item.connect(target.item.single())

        # ignore at the moment segment selector
        anno.targets.connect(target)

        for body in bodies:
            if body['type'] != 'TextualBody':
                raise ValueError('Invalid body for description annotation: {}'
                                 .format(body['type']))
            text_lang = body.get('language')
            bodyNode = TextualBody(
                value=body['value'], language=text_lang).save()
            anno.bodies.connect(bodyNode)

        return anno

    def create_link_annotation(self, user, bodies, target, selector,
                               is_private=False, embargo_date=None):
        '''
        Create a link annotation.
        '''
        visibility = 'private' if is_private else 'public'
        log.debug("Create a new {} description annotation".format(visibility))
        # create annotation node
        anno = Annotation(annotation_type='LNK', private=is_private).save()
        if embargo_date is not None:
            anno.embargo = embargo_date
            anno.save()
        # should we allow to create anno without a user of the system?
        if user is not None:
            anno.creator.connect(user)

        if isinstance(target, Item):
            anno.source_item.connect(target)
        elif isinstance(target, Annotation):
            anno.source_item.connect(target.source_item.single())
        elif isinstance(target, Shot):
            anno.source_item.connect(target.item.single())

        # ignore at the moment segment selector
        if selector is not None:
            log.warn('Selector not yet applicable for the target {0}'
                     .format(target))
        anno.targets.connect(target)

        # ONLY textual and reference body allowed at the moment
        for body in bodies:
            if body['type'] == 'TextualBody':
                bodyNode = TextualBody(value=body['value']).save()
            elif body['type'] == 'BibliographicReference':
                properties = body['value']
                bodyNode = BibliographicReference(**properties).save()
            else:
                raise ValueError('Invalid body for link annotation: {}'
                                 .format(body['type']))
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
        return False if (len(node.annotation.all()) > 1 or len(node.annotation_body.all())) else True

    @graph_transactions
    def create_automatic_tvs(self, item, shots):
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
        for shot_num, properties in shots.items():
            properties['shot_num'] = shot_num
            shot = self.graph.Shot(**properties).save()
            tvs_body.segments.connect(shot)
            item.shots.connect(shot)

    @graph_transactions
    def update_automatic_tvs(self, item, shots, vim_estimations, rev=False, reviser=None):
        '''
        This procedure updates the automatic shot list preserving existing
        annotations such as TAG, DSC, LNK etc.

        For each incoming shot it updates the corresponding shot in the
        database with the same shot_num. If a new shot occurs, it is added to
        the actual list. If instead the list of shots is shortened, all shot in
        excess will be removed.

        Regarding existing annotations, for the manual ones, this procedure
        expects the binding passed as argument. The shots parameter conveys
        together with shot info also the releted manual annotations (list of
        anno IDs).
        If an bad annotation ID is passed (it doesn't belong to any shot) it is
        ignored. If instead some of the existing annotations are not passed,
        then these "orphan" annotations are deleted.

        On the other hand, for automatic annotations, the segments are
        reorganized after updating the shot list. The segments are reassigned
        to the shots (WITHIN_SHOT) after updating the list of cuts.
        '''
        log.info('Update existing shot list preserving anno(s).')
        FHG_TVS = item.targeting_annotations.search(
            annotation_type='TVS', generator='FHG')
        if not FHG_TVS:
            raise ValueError('Expected TVS anno from FHG.')

        tvs = FHG_TVS[0]
        tvs_body = tvs.bodies.single().downcast()

        existing_shots = item.shots.all()
        old_size = len(existing_shots)
        log.debug('Existing shot list size: {}'.format(old_size))
        new_size = len(shots)
        log.debug('Incoming shot list size: {}'.format(new_size))

        # for each existing shot we gather and disconnect from them all the
        # manual annotations
        existing_annotations = []
        for old_shot in existing_shots:
            for a in old_shot.annotation.search(generator__isnull=True):
                existing_annotations.append(a)
                old_shot.annotation.disconnect(a)
        log.info('total existing annotations: %s' % len(existing_annotations))

        # foreach incoming shot
        log.debug('----------')
        current_time = datetime.now(pytz.utc)
        for shot_num, properties in shots.items():
            shot_node = None
            res = item.shots.search(shot_num=shot_num)
            if not res:
                # new incoming shot:
                # rarely expected (especially for framerate fix)
                log.info('New incoming shot number: {}'.format(shot_num))
                shot_node = self.graph.Shot(
                    shot_num=shot_num, **properties)
                if rev and 'revision_confirmed' in properties:
                    shot_node.revision_confirmed = properties['revision_confirmed']
                if rev and 'revision_check' in properties:
                    shot_node.revision_check = properties['revision_check']
                shot_node.save()
                if reviser is not None and shot_node.revision_confirmed:
                    shot_node.revised_by.connect(reviser,
                                                 {'when': current_time})
                tvs_body.segments.connect(shot_node)
                item.shots.connect(shot_node)
            else:
                shot_node = res[0]
                # props to update
                if rev and 'revision_confirmed' in properties:
                    previous_confirmed = shot_node.revision_confirmed
                    shot_node.revision_confirmed = properties['revision_confirmed']
                    if reviser is not None and ((not previous_confirmed and shot_node.revision_confirmed) or
                                                properties['start_frame_idx'] != shot_node.start_frame_idx):
                        shot_node.revised_by.connect(reviser,
                                                     {'when': current_time})
                    if 'revision_check' in properties:
                        shot_node.revision_check = properties['revision_check']
                shot_node.start_frame_idx = properties['start_frame_idx']
                shot_node.end_frame_idx = properties['end_frame_idx']
                shot_node.timestamp = properties['timestamp']
                shot_node.duration = properties['duration']
                shot_node.thumbnail_uri = properties['thumbnail_uri']
                shot_node.save()
            # manage annotations
            if 'annotations' in properties:
                for anno_id in properties['annotations']:
                    # look up ID from existing_annotations
                    log.debug('look up for annotation ID %s' % anno_id)
                    found = [x for x in existing_annotations if x.uuid == anno_id]
                    if len(found) == 0:
                        continue
                    found[0].targets.connect(shot_node)
            log.debug(shot_node)
            log.debug('----------')
        if old_size > new_size:
            # delete exceeding shots
            # NOTE: we can do this because no annotation targets the shot
            log.warn('The shot list [size={new_size}] is shorter than the '
                     'previous one [size={old_size}]'.format(
                         new_size=new_size, old_size=old_size))
            for i in range(new_size, old_size):
                shot_to_delete = item.shots.search(shot_num=i)
                log.warn('Exceeding shot to delete: {}'.format(shot_to_delete))
                shot_to_delete[0].delete()

        # clean-up "orphan" manual annotations
        for anno in existing_annotations:
            try:
                anno.targets.all()
            except CardinalityViolation:
                log.warn('orphan annotation to delete: {}'.format(anno))
                # delete anno
                # NOTE: this could occur if an exisitng manual anno is not
                # passed in the shot revision request.
                bodies = anno.bodies.all()
                for b in bodies:
                    original_body = b.downcast()
                    if isinstance(original_body, ResourceBody):
                        # disconnect this body
                        anno.bodies.disconnect(b)
                    else:
                        b.delete()
                anno.delete()

        # rearrange the relationships between existing segments and the new
        # shot list
        self.arrange_video_segments(item)

    def arrange_video_segments(self, item):
        '''
        Rearrange the relationships between existing segments and the new shots
        (:VideoSegment)-[:WITHIN_SHOT]->(:Shot)
        '''
        query = "MATCH (i:Item {{uuid: '{item_id}'}})<-[:SOURCE]-(anno:Annotation {{annotation_type:'TAG', generator:'FHG'}}) " \
                "MATCH (anno)-[:HAS_TARGET]->(sgm:VideoSegment) WHERE NOT sgm:Shot " \
                "RETURN sgm"
        results = self.graph.cypher(query.format(
            item_id=item.uuid))
        segments = [self.graph.VideoSegment.inflate(row[0]) for row in results]
        for segment in segments:
            # disconnect the segment from its current shots
            segment.within_shots.disconnect_all()
            # re-connect the shot where the segment is enclosed
            shots = self.get_enclosing_shots(segment, item)
            if shots is None or len(shots) == 0:
                raise ValueError('Invalid state: cannot be found shot(s) enclosing '
                                 'selected segment [t={start},{end}]'
                                 .format(start=segment.start_frame_idx, end=segment.end_frame_idx))
            for shot in shots:
                segment.within_shots.connect(shot)

    def create_tvs_manual_annotation(self, user, bodies, target,
                                     is_private=False, embargo_date=None):
        '''
        Create a new user manual segmentation for this video. One segmentation
        per user is allowed at the moment.
        '''
        if not isinstance(target, Item):
            raise ValueError('Segmentation allowed only for Item target.')
        # look for existing segmentation for the given user
        segmentation = self.lookup_existing_user_segmentation(user, target)
        if segmentation is not None:
            raise DuplicatedAnnotationError('Segmentation for user<{email}> '
                                            'does already exist for item [{item_id}].'
                                            .format(email=user.email, item_id=target.uuid))
        visibility = 'private' if is_private else 'public'
        log.debug("Create a new {} segmentation annotation".format(visibility))
        # create annotation node
        anno = Annotation(annotation_type='TVS', private=is_private).save()
        if embargo_date is not None:
            anno.embargo = embargo_date
            anno.save()
        anno.creator.connect(user)
        anno.source_item.connect(target)
        anno.targets.connect(target)

        # Expected single body
        body = bodies[0]
        if body['type'] != 'TVSBody':
            raise ValueError('Invalid body for segmentation annotation: {}'
                             .format(body['type']))
        tvs_body = TVSBody().save()
        anno.bodies.connect(tvs_body)
        segments = body.get('segments')
        if segments is None or type(segments) is not list or len(segments) == 0:
            raise ValueError('Invalid segments')
        for s in segments:
            s_start, s_end = map(
                int, s.lstrip('t=').split(','))
            log.debug('start:{}, end:{}'.format(s_start, s_end))
            if s_start > s_end:
                raise ValueError(
                    'Invalid segment range. The start is greater than the end.')
            # search for existing segment for the given item
            segment = self.lookup_existing_segment(s_start, s_end, target)
            log.debug('Segment does exist? {}'.format(
                True if segment else False))
            if segment is None:
                segment = VideoSegment(
                    start_frame_idx=s_start, end_frame_idx=s_end).save()
                # look up the shot where the segment is enclosed
                shots = self.get_enclosing_shots(segment, target)
                if shots is None or len(shots) == 0:
                    raise ValueError('Invalid state: cannot be found shot(s) enclosing '
                                     'selected segment [{0}]'.format(s))
                for shot in shots:
                    segment.within_shots.connect(shot)
            tvs_body.segments.connect(segment)

        return anno

    @graph_transactions
    def delete_tvs_annotation(self, annotation):
        log.debug('Delete existing TVS annotation')
        body = annotation.bodies.single()
        if body:
            tvs_body = body.downcast()
            for segment in tvs_body.segments:
                # avoid illegal state with orphan annotations
                annotations = segment.annotation.all()
                if annotations is not None and len(annotations) > 0:
                    raise ValueError('TVS annotation [{anno_id}] cannot be'
                                     ' deleted because referred by one or more'
                                     ' other annotations'.format(anno_id=annotation.uuid))
                segment.delete()
            tvs_body.delete()
        annotation.delete()

    @graph_transactions
    def delete_tvs_manual_annotation(self, annotation):
        log.debug('Delete existing manual TVS annotation')
        body = annotation.bodies.single()
        tvs_body = body.downcast()
        for segment in tvs_body.segments:
            # check if the segment is annotated
            annotations = segment.annotation.all()
            segmentations = segment.annotation_body.all()
            if len(annotations) > 0 or len(segmentations) > 1:
                # there exist related annotations or this segment is shared by
                # some other segmentations: just disconnect the node.
                tvs_body.segments.disconnect(segment)
            else:
                segment.delete()
        tvs_body.delete()
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
            log.debug(type(original_vim_body))
            original_vim_body.delete()
        annotation.delete()

    @graph_transactions
    def delete_auto_annotation(self, annotation):
        log.debug('Delete existing automatic TAG annotation')
        body = annotation.bodies.single()
        object_id = None
        object_type = None
        if body:
            od_body = body.downcast()
            object_id = od_body.object_id
            concept = None
            try:
                concept = od_body.object_type.single()
            except Exception as e:
                log.warning(e)
            if concept is not None:
                object_type = concept.name
            od_body.delete()
        refined_selection = annotation.refined_selection.single()
        if refined_selection:
            sequence_selector = refined_selection.downcast()
            sequence_selector.delete()
        # delete any orphan video segments (NOT SHOT!)
        targets = annotation.targets.all()
        for t in targets:
            target_labels = t.labels()
            log.debug("Target label(s): {}".format(target_labels))
            if 'VideoSegment' in target_labels and \
                    'Shot' not in target_labels and \
                    self.is_orphan_segment(t.downcast(target_class='VideoSegment')):
                t.delete()
                log.debug('Deleted orphan segment')
        annotation.delete()
        log.info(
            'Automatic TAG[{oid}/{otype}] deleted.'.format(oid=object_id, otype=object_type))

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
        # log.debug("Filtered bodies: {0}".format(filtered_bodies))
        return warnings, filtered_bodies

    def get_enclosing_shots(self, segment, item):
        '''
        Return the shot list of the item enclosing the given segment.
        '''
        if item is None or not isinstance(item, Item) or item.item_type != 'Video':
            raise ValueError('Invalid item in getting enclosing shots.')
        s_start = segment.start_frame_idx
        s_end = segment.end_frame_idx
        shots = []
        for s in sorted(item.shots, key=lambda k: k.start_frame_idx):
            if (
                (s_start >= s.start_frame_idx and s_start <= s.end_frame_idx) or
                (s_end >= s.start_frame_idx and s_end <= s.end_frame_idx) or
                (s_start < s.start_frame_idx and s_end > s.end_frame_idx)
            ):
                shots.append(s)
        return shots

    def lookup_existing_user_segmentation(self, user, item):
        '''
        Lookup for existing user segmentation for a given item.
        '''
        query = "MATCH (anno:Annotation {{annotation_type:'TVS'}})" \
                "-[:IS_ANNOTATED_BY]->(:User {{uuid:'{user_id}'}}) " \
                "MATCH (anno)-[:HAS_TARGET]->(:Item {{uuid:'{item_id}'}}) " \
                "RETURN anno"
        results = self.graph.cypher(query.format(
            user_id=user.uuid, item_id=item.uuid))
        anno = [self.graph.Annotation.inflate(row[0]) for row in results]
        return anno[0] if anno else None

    def lookup_existing_segment(self, start_frame, end_frame, item):
        '''
        Search for existing segment for a given item.
        NOTE: we're excluding shots!
        '''
        query = "MATCH (n:VideoSegment) WHERE n.start_frame_idx={start_frame} AND n.end_frame_idx={end_frame} " \
                "MATCH (n)-[:WITHIN_SHOT]-(s:Shot)-[:SHOT]-(i:Item {{uuid: '{item_id}'}}) " \
                "RETURN n"
        results = self.graph.cypher(query.format(
            start_frame=start_frame, end_frame=end_frame, item_id=item.uuid))
        segment = [self.graph.VideoSegment.inflate(row[0]) for row in results]
        return segment[0] if segment else None

    def check_automatic_tagging(self, item_id):
        '''
        Check if at least one automatic annotation exists for the given content
        item.
        '''
        query = "MATCH (a:Annotation {{annotation_type:'TAG'}})-[:SOURCE]-(i:Item {{uuid:'{item_id}'}}) " \
                "WHERE a.generator IS NOT NULL " \
                "RETURN count(a)"
        results = self.graph.cypher(query.format(item_id=item_id))
        count = [row[0] for row in results][0]
        log.debug("Number of automatic annotations found: {0}".format(count))
        return True if count > 0 else False

    def check_automatic_od(self, item_id):
        '''
        Check if at least one automatic object detection exists for the given
        content item.
        '''
        query = "MATCH (a:Annotation {{annotation_type:'TAG'}})-[:SOURCE]-(i:Item {{uuid:'{item_id}'}}) " \
                "WHERE a.generator IS NOT NULL " \
                "MATCH (a)-[:HAS_BODY]-(b:ODBody) WHERE NOT b:BRBody " \
                "RETURN count(a)"
        results = self.graph.cypher(query.format(item_id=item_id))
        count = [row[0] for row in results][0]
        log.debug("Number of automatic object detections found: {0}".format(count))
        return True if count > 0 else False

    def check_automatic_br(self, item_id):
        '''
        Check if at least one automatic building recognition exists for the
        given content item.
        '''
        query = "MATCH (a:Annotation {{annotation_type:'TAG'}})-[:SOURCE]-(i:Item {{uuid:'{item_id}'}}) " \
                "WHERE a.generator IS NOT NULL " \
                "MATCH (a)-[:HAS_BODY]-(BRBody) " \
                "RETURN count(a)"
        results = self.graph.cypher(query.format(item_id=item_id))
        count = [row[0] for row in results][0]
        log.debug("Number of automatic building recognitions found: {0}".format(count))
        return True if count > 0 else False

    def remove_segment(self, anno, segment):
        '''
        Remove a segment for a given segmentation (TVS anno).
        Keep in mind that at least one segment MUST exist in the segmentation.
        Only disconnect the segment if it belongs to some other segmentation(s)
        and/or is targeted by some TAG annotations.
        '''
        if anno is None or anno.annotation_type != 'TVS':
            raise ValueError('Invalid annotation')
        # check if the segment belongs to the actual segmentation
        bodies = anno.bodies.all()
        tvs_body = bodies[0].downcast()
        found = False
        segments = tvs_body.segments
        for s in segments:
            if s.uuid == segment.uuid:
                found = True
                break
        if not found:
            raise ValueError(
                "Segment [{}] does NOT belong to this segmentation".format(segment.uuid))

        # check if the segment is the last
        log.debug('actual segmentation list size: {size}'.format(
            size=len(segments)))
        if len(segments) == 1:
            raise DuplicatedAnnotationError("Cannot remove the last segment. "
                                            "Remove the segmentation itself instead")

        # check if the segment is annotated
        annotations = segment.annotation.all()
        segmentations = segment.annotation_body.all()
        if len(annotations) > 0 or len(segmentations) > 1:
            # there exist related annotations or this segment is shared by
            # some other segmentations: just disconnect the node.
            tvs_body.segments.disconnect(segment)
        else:
            segment.delete()

    def add_segment(self, anno, value):
        '''
        Add a new segment to a given segmentation.
        '''
        if anno is None or anno.annotation_type != 'TVS':
            raise ValueError('Invalid annotation')
        s_start, s_end = map(
            int, value.lstrip('t=').split(','))
        body = anno.bodies.single()
        tvs_body = body.downcast()
        # look for existing segment in the segmentation
        segments = tvs_body.segments.all()
        for s in segments:
            log.debug(s)
            if s.start_frame_idx == s_start and s.end_frame_idx == s_end:
                raise DuplicatedAnnotationError('Segment [t={start},{end}] does already exist'
                                                .format(start=s_start, end=s_end))

        # search for existing segment for the given item
        item = anno.source_item.single()
        segment = self.lookup_existing_segment(s_start, s_end, item)
        log.debug('Segment does exist? {}'.format(
            True if segment else False))
        if segment is None:
            segment = VideoSegment(
                start_frame_idx=s_start, end_frame_idx=s_end).save()
            # look up the shot where the segment is enclosed
            shots = self.get_enclosing_shots(segment, item)
            if shots is None or len(shots) == 0:
                raise ValueError('Invalid state: cannot be found shot(s) enclosing '
                                 'selected segment [t={start},{end}]'
                                 .format(start=s_start, end=s_end))
            for shot in shots:
                segment.within_shots.connect(shot)
        tvs_body.segments.connect(segment)


class DuplicatedAnnotationError(Exception):
    pass
