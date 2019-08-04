# -*- coding: utf-8 -*-
from utilities.logs import get_logger

log = get_logger(__name__)


class Initializer(object):
    def __init__(self, services):

        self.neo4j = services['neo4j']

        Role = self.neo4j.Role
        Group = self.neo4j.Group
        Provider = self.neo4j.Provider

        try:
            Role.nodes.get(name='local_admin')
            log.debug("Coordinator role already exists")
        except Role.DoesNotExist:
            local_admin = Role()
            local_admin.name = 'local_admin'
            local_admin.description = 'Coordinator'
            local_admin.save()
            log.info("Coordinator role successfully created")

        try:
            Role.nodes.get(name='Archive')
            log.debug("Archive role already exists")
        except Role.DoesNotExist:
            archiver = Role()
            archiver.name = 'Archive'
            archiver.description = 'Archive'
            archiver.save()
            log.info("Archive role successfully created")

        try:
            Role.nodes.get(name='Researcher')
            log.debug("Researcher role already exists")
        except Role.DoesNotExist:
            researcher = Role()
            researcher.name = 'Researcher'
            researcher.description = 'Researcher'
            researcher.save()
            log.info("Researcher role successfully created")

        try:
            Role.nodes.get(name='Reviser')
            log.debug("Reviser role already exists")
        except Role.DoesNotExist:
            reviser = Role()
            reviser.name = 'Reviser'
            reviser.description = 'Reviser'
            reviser.save()
            log.info("Reviser role successfully created")

        try:
            admin = Role.nodes.get(name='admin_root')
            admin.description = 'Admin'
            admin.save()
            log.info("Admin role successfully updated")
        except Role.DoesNotExist:
            log.warning("Admin role does not exist")

        if len(Group.nodes) > 0:
            log.info("Found one or more already defined groups")
        else:
            log.warning("No group defined")
            group = Group()
            group.fullname = "test"
            group.shortname = "test"
            group.save()

            group = Group()
            group.fullname = "Default user group"
            group.shortname = "default"
            group.save()

            log.info("Groups successfully created")

        # Providers
        try:
            Provider.nodes.get(identifier='CCB')
            log.debug("Provider CCB already exists")
        except Provider.DoesNotExist:
            ccb = Provider()
            ccb.identifier = 'CCB'
            ccb.scheme = 'ACRO'
            ccb.name = 'Fondazione Cineteca di Bologna'
            ccb.city = 'Bologna'
            ccb.address = 'Via Riva di Reno, 72, 40122 Bologna BO, Italy'
            ccb.phone = '+39 (0) 512194820'
            ccb.fax = '+39 (0) 512194821'
            ccb.email = 'cinetecadirezione@cineteca.bologna.it'
            ccb.website = 'www.cinetecadibologna.it'
            ccb.save()
            log.info("Provider CCB successfully created")

        try:
            Provider.nodes.get(identifier='TTE')
            log.debug("Provider TTE already exists")
        except Provider.DoesNotExist:
            tte = Provider()
            tte.identifier = 'TTE'
            tte.scheme = 'ACRO'
            tte.name = 'Tainiothiki tis Ellados'
            tte.city = 'Athens'
            tte.address = 'Iera Odos 48 and Megalou Alexandrou 134-136 10435 Athens'
            tte.phone = '+30 210 3612046'
            tte.fax = '+39 210 3628468'
            tte.email = 'nina@tainiothiki.gr'
            tte.website = 'www.tainiothiki.gr'
            tte.save()
            log.info("Provider TTE successfully created")

        try:
            Provider.nodes.get(identifier='CRB')
            log.debug("Provider CRB already exists")
        except Provider.DoesNotExist:
            crb = Provider()
            crb.identifier = 'CRB'
            crb.scheme = 'ACRO'
            crb.name = 'Cinémathèque Royale de Belgique'
            crb.city = 'Brussels'
            crb.address = 'Rue Ravenstein 3, 1000 Bruxelles, Belgium'
            crb.phone = '+32 (0) 25511900'
            crb.fax = '+32 (0) 25511907'
            crb.email = 'info@cinematek.be'
            crb.website = 'www.cinematek.be'
            crb.save()
            log.info("Provider CRB successfully created")

        try:
            Provider.nodes.get(identifier='SFI')
            log.debug("Provider SFI already exists")
        except Provider.DoesNotExist:
            sfi = Provider()
            sfi.identifier = 'SFI'
            sfi.scheme = 'ACRO'
            sfi.name = 'Svenska Filminstitutet'
            sfi.city = 'Stockholm'
            sfi.address = 'Box 27 126, 102 52 Stockholm, Sweden'
            sfi.phone = '08-665 11 00'
            sfi.email = 'filmarkivet.se@filminstitutet.se'
            sfi.website = 'www.filminstitutet.se'
            sfi.save()
            log.info("Provider SFI successfully created")

        try:
            Provider.nodes.get(identifier='DFI')
            log.debug("Provider DFI already exists")
        except Provider.DoesNotExist:
            dfi = Provider()
            dfi.identifier = 'DFI'
            dfi.scheme = 'ACRO'
            dfi.name = 'Det Danske Filminstitut'
            dfi.city = 'Copenhagen'
            dfi.address = 'Gothersgade 55, DK-1123 Copenhagen K, Denmark'
            dfi.phone = '+45 33743400'
            dfi.fax = '+45 33743403'
            dfi.email = 'dfi@dfi.dk'
            dfi.website = 'www.dfi.dk'
            dfi.save()
            log.info("Provider DFI successfully created")

        try:
            Provider.nodes.get(identifier='DIF')
            log.debug("Provider DIF already exists")
        except Provider.DoesNotExist:
            dif = Provider()
            dif.identifier = 'DIF'
            dif.scheme = 'ACRO'
            dif.name = 'Deutsches Filminstitut'
            dif.city = 'Frankfurt'
            dif.address = 'Schaumainkai 41, 60596 Frankfurt am Main, Germany'
            dif.phone = '+49 69 961220 403'
            dif.fax = '+49 69 961220 999'
            dif.email = 'richter@deutsches-filminstitut.de'
            dif.website = 'www.deutsches-filminstitut.de'
            dif.save()
            log.info("Provider DIF successfully created")

        try:
            Provider.nodes.get(identifier='OFM')
            log.debug("Provider OFM already exists")
        except Provider.DoesNotExist:
            ofm = Provider()
            ofm.identifier = 'OFM'
            ofm.scheme = 'ACRO'
            ofm.name = 'Österreichisches Filmmuseum'
            ofm.city = 'Vienna'
            ofm.address = 'Augustinerstraße 1, 1010 Vienna, Austria'
            ofm.phone = '+43 1 533 70 54'
            ofm.fax = '+43 1 533 70 54 25'
            ofm.website = 'www.filmmuseum.at'
            ofm.save()
            log.info("Provider OFM successfully created")

        try:
            Provider.nodes.get(identifier='WSTLA')
            log.debug("Provider WSTLA already exists")
        except Provider.DoesNotExist:
            ofm = Provider()
            ofm.identifier = 'WSTLA'
            ofm.scheme = 'ACRO'
            ofm.name = 'Wiener Stadt- und Landesarchiv'
            ofm.city = 'Vienna'
            ofm.address = 'Gasometer D | Guglgasse 14, A-1110 Wien, Austria'
            ofm.phone = '+43 1 4000 84808 | +43 1 4000 84819'
            ofm.fax = '+43 1 4000 84809'
            ofm.email = 'post@ma08.wien.gv.at'
            ofm.save()
            log.info("Provider OFM successfully created")

        try:
            Provider.nodes.get(identifier='FDC')
            log.debug("Provider FDC already exists")
        except Provider.DoesNotExist:
            fdc = Provider()
            fdc.identifier = 'FDC'
            fdc.scheme = 'ACRO'
            fdc.name = 'Filmoteca de Catalunya'
            fdc.city = 'Barcelona'
            fdc.address = 'Plaça Salvador Seguí, 1 – 9, 08001 Barcelona, Spain'
            fdc.phone = '+34 935 671 070'
            fdc.website = 'www.filmoteca.cat'
            fdc.save()
            log.info("Provider FDC successfully created")

        try:
            Provider.nodes.get(identifier='MNC')
            log.debug("Provider MNC already exists")
        except Provider.DoesNotExist:
            mnc = Provider()
            mnc.identifier = 'MNC'
            mnc.scheme = 'ACRO'
            mnc.name = 'Museo Nazionale del Cinema'
            mnc.city = 'Turin'
            mnc.address = 'Via Montebello, 20 10124 Torino, Italia'
            mnc.phone = '+39 011.8138.580'
            mnc.fax = '+39 011 8138 585'
            mnc.email = 'cineteca@museocinema.it'
            mnc.website = 'http://www.museocinema.it'
            mnc.save()
            log.info("Provider MNC successfully created")


class Customizer(object):
    def custom_user_properties(self, properties):
        return properties

    def custom_post_handle_user_input(self, auth, user_node, properties):

        try:
            group = auth.db.Group.nodes.get(shortname="default")
        except auth.db.Group.DoesNotExist:
            log.warning("Unable to find default group, creating")
            group = auth.db.Group()
            group.fullname = "Default user group"
            group.shortname = "default"
            group.save()

        log.info("Link %s to group %s", user_node.email, group.shortname)
        user_node.belongs_to.connect(group)

        return True
