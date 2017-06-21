
from rapydo.utils.logs import get_logger
from neomodel import db

from imc.models.neo4j import (
    Annotation, TVSBody, VIMBody
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
        annotation.source_item.connect(item)

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
        log.info('Delete existing TVS annotation')
        tvs_body = annotation.bodies.single()
        if tvs_body:
            original_tvs_body = tvs_body.downcast()
            log.info(original_tvs_body.__class__)
            for segment in original_tvs_body.segments:
                segment.delete()
            original_tvs_body.delete()
        annotation.delete()

    @db.transaction
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

    @db.transaction
    def delete_vim_annotation(self, annotation):
        log.info('Delete existing VIM annotation')
        vim_body = annotation.bodies.single()
        if vim_body:
            original_vim_body = vim_body.downcast()
            log.info(original_vim_body.__class__)
            original_vim_body.delete()
        annotation.delete()
