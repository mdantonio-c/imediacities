
from rapydo.utils.logs import get_logger

log = get_logger(__name__)


class Initializer(object):

    def __init__(self, services):

        self.neo4j = services['neo4j']

        Role = self.neo4j.Role

        try:
            Role.nodes.get(name='Archive')
            log.debug("Archive role already exists")
        except Role.DoesNotExist:
            archiver = Role()
            archiver.name ='Archive'
            archiver.description = \
                'Role allowed to upload contents and metadata'
            archiver.save()
            log.info("Archive role successfully created")

        try:
            Role.nodes.get(name='Researcher')
            log.debug("Researcher role already exists")
        except Role.DoesNotExist:
            researcher = Role()
            researcher.name ='Researcher'
            researcher.description ='Researcher'
            researcher.save()
            log.info("Researcher role successfully created")

        try:
            admin = Role.nodes.get(name='admin_root')
            admin.description ='Admin'
            admin.save()
            log.info("Admin role successfully updated")
        except Role.DoesNotExist:
            log.warning("Admin role does not exist")