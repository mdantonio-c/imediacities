# -*- coding: utf-8 -*-
"""
    security.authz
    ~~~~~~~~~~~~~~
    Simple authz decorator for making content access control decision.

"""
from imc.tasks.services.creation_repository import CreationRepository
from restapi.exceptions import RestApiException
from utilities import htmlcodes as hcodes
from utilities.logs import get_logger

logger = get_logger(__name__)


def pre_authorize(func):

    def _is_public_domain(rs):
        return True if (
            rs == "02" or  # EU Orphan Work
            rs == "04" or  # In copyright - Non-commercial use permitted
            rs == "05" or  # Public Domain
            rs == "06" or  # No Copyright - Contractual Restrictions
            rs == "07" or  # No Copyright - Non-Commercial Use Only
            rs == "08" or  # No Copyright - Other Known Legal Restrictions
            rs == "09"     # No Copyright - United States
        ) else False

    def _is_general_public(user):
        """User is general public if anonymous (not logged in) or is a 'normal
        user'.
        """
        return True if (user is None or
                        user.roles.search(name='normal_user')) else False

    def has_permission(self, **kwargs):
        """verify if user has permission to access the specified content id"""
        entity_id = kwargs.get('video_id') or kwargs.get('image_id')
        if entity_id is None:
            return
        user = self.get_user_if_logged()
        logger.debug('Logged in user: {}'.format(user))
        logger.debug("Has permission to access entity[{}]?".format(entity_id))
        self.graph = self.get_service_instance('neo4j')
        repo = CreationRepository(self.graph)
        rs = repo.get_right_status(entity_id)
        logger.debug('right status = {}'.format(rs))
        """
        ('01', 'In copyright'),
        ('02', 'EU Orphan Work'),
        ('03', 'In copyright - Educational use permitted'),
        ('04', 'In copyright - Non-commercial use permitted'),
        ('05', 'Public Domain'),
        ('06', 'No Copyright - Contractual Restrictions'),
        ('07', 'No Copyright - Non-Commercial Use Only'),
        ('08', 'No Copyright - Other Known Legal Restrictions'),
        ('09', 'No Copyright - United States'),
        ('10', 'Copyright Undetermined')
        """
        # logger.debug('Is public domain? {}'.format(_is_public_domain(rs)))
        if _is_general_public(user) and not _is_public_domain(rs):
            raise RestApiException(
                "User is not authorized to access content",
                status_code=hcodes.HTTP_BAD_FORBIDDEN)
        return func(self, entity_id)

    return has_permission
