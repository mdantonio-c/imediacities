"""
    security.authz
    ~~~~~~~~~~~~~~
    Simple authz decorator for making content access control decision.

"""
from imc.tasks.services.creation_repository import CreationRepository
from restapi.connectors import neo4j
from restapi.exceptions import Forbidden
from restapi.services.authentication import Role
from restapi.utilities.logs import log


def pre_authorize(func):
    def _is_public_domain(rs):
        return (
            True
            if (
                rs == "02"
                or rs == "04"  # EU Orphan Work
                or rs == "05"  # In copyright - Non-commercial use permitted
                or rs == "06"  # Public Domain
                or rs == "07"  # No Copyright - Contractual Restrictions
                or rs == "08"  # No Copyright - Non-Commercial Use Only
                or rs  # No Copyright - Other Known Legal Restrictions
                == "09"  # No Copyright - United States
            )
            else False
        )

    def _is_general_public(user):
        """User is general public if anonymous (not logged in) or is a 'normal
        user'.
        """
        return True if (user is None or user.roles.search(name=Role.USER)) else False

    def _has_rights(self, user, entity_id):
        """
        Look at right status
        """
        self.graph = neo4j.get_instance()
        repo = CreationRepository(self.graph)
        rs = repo.get_right_status(entity_id)
        log.debug("right status = {}", rs)
        return False if _is_general_public(user) and not _is_public_domain(rs) else True

    def _has_public_access(self, user, entity_id):
        """
        Look at public access flag
        """
        if not _is_general_public(user):
            return True
        self.graph = neo4j.get_instance()
        repo = CreationRepository(self.graph)
        return repo.publicly_accessible(entity_id)

    def has_permission(self, **kwargs):
        """verify if user has permission to access the specified content id"""
        entity_id = kwargs.get("video_id") or kwargs.get("image_id")

        if entity_id is None:
            # do not yet raise the exception but ignore it
            return func(self, **kwargs)

        ct = kwargs.get("content_type")
        if ct is None or (ct != "image" and ct != "video"):
            # do not yet raise the exception but ignore it
            return func(self, **kwargs)
        user = self.get_user()
        # log.debug("Logged in user: {}", user)
        # log.debug("Has permission to access entity[{}]?", entity_id)
        if not _has_public_access(self, user, entity_id):
            raise Forbidden("User is not authorized to access content")

        return func(self, **kwargs)

    return has_permission
