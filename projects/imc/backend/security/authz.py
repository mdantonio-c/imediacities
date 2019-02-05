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

    def _has_rights(self, user, entity_id):
        """
        Look at right status
        """
        self.graph = self.get_service_instance('neo4j')
        repo = CreationRepository(self.graph)
        rs = repo.get_right_status(entity_id)
        logger.debug('right status = {}'.format(rs))
        return (False if _is_general_public(user) and not _is_public_domain(rs)
                else True)

    def _has_public_access(self, user, entity_id):
        """
        Look at public access flag
        """
        if not _is_general_public(user):
            return True
        self.graph = self.get_service_instance('neo4j')
        repo = CreationRepository(self.graph)
        return repo.publicly_accessible(entity_id)

    def has_permission(self, **kwargs):
        """verify if user has permission to access the specified content id"""
        entity_id = kwargs.get('video_id') or kwargs.get('image_id')
        if entity_id is None:
            # do not yet raise the exception but ignore it
            return func(self, entity_id)
        params = self.get_input()
        ct = params['type']
        if ct is None or (ct != 'image' and ct != 'video'):
            # do not yet raise the exception but ignore it
            return func(self, entity_id)
        user = self.get_user_if_logged()
        logger.debug('Logged in user: {}'.format(user))
        logger.debug("Has permission to access entity[{}]?".format(entity_id))
        if not _has_public_access(self, user, entity_id):
            raise RestApiException(
                "User is not authorized to access content",
                status_code=hcodes.HTTP_BAD_FORBIDDEN)

        return func(self, entity_id)

    return has_permission
