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
            admin = Role.nodes.get(name='admin_root')
            admin.description = 'Admin'
            admin.save()
            log.info("Admin role successfully updated")
        except Role.DoesNotExist:
            log.warning("Admin role does not exist")

        if (len(Group.nodes) > 0):
            log.info("Found one ore more groups already defined")
        else:
            log.warning("No group defined")
            group = Group()
            group.fullname = "test"
            group.shortname = "test"
            group.save()
            log.info("Group successfully created")

        # Providers
        try:
            Provider.nodes.get(identifier='CCB')
            log.debug("Provider CCB already exists")
        except Provider.DoesNotExist:
            ccb = Provider()
            ccb.identifier = 'CCB'
            ccb.scheme = 'ACRO'
            ccb.name = 'Fondazione Cineteca di Bologna'
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
            ccb = Provider()
            ccb.identifier = 'TTE'
            ccb.scheme = 'ACRO'
            ccb.name = 'Tainiothiki tis Ellados'
            ccb.address = 'Iera Odos 48 and Megalou Alexandrou 134-136 10435 Athens'
            ccb.phone = '+30 210 3612046'
            ccb.fax = '+39 210 3628468'
            ccb.email = 'nina@tainiothiki.gr'
            ccb.website = 'www.tainiothiki.gr'
            ccb.save()
            log.info("Provider TTE successfully created")

        try:
            Provider.nodes.get(identifier='CRB')
            log.debug("Provider CRB already exists")
        except Provider.DoesNotExist:
            ccb = Provider()
            ccb.identifier = 'CRB'
            ccb.scheme = 'ACRO'
            ccb.name = 'Cinémathèque Royale de Belgique'
            ccb.address = 'Rue Ravenstein 3, 1000 Bruxelles, Belgium'
            ccb.phone = '+32 (0) 25511900'
            ccb.fax = '+32 (0) 25511907'
            ccb.email = 'info@cinematek.be'
            ccb.website = 'www.cinematek.be'
            ccb.save()
            log.info("Provider CRB successfully created")

        try:
            Provider.nodes.get(identifier='SFI')
            log.debug("Provider SFI already exists")
        except Provider.DoesNotExist:
            ccb = Provider()
            ccb.identifier = 'SFI'
            ccb.scheme = 'ACRO'
            ccb.name = 'Svenska Filminstitutet'
            ccb.address = 'Box 27 126, 102 52 Stockholm, Sweden'
            ccb.phone = '08-665 11 00'
            ccb.email = 'filmarkivet.se@filminstitutet.se'
            ccb.website = 'www.filminstitutet.se'
            ccb.save()
            log.info("Provider SFI successfully created")

        try:
            Provider.nodes.get(identifier='DFI')
            log.debug("Provider DFI already exists")
        except Provider.DoesNotExist:
            ccb = Provider()
            ccb.identifier = 'DFI'
            ccb.scheme = 'ACRO'
            ccb.name = 'Det Danske Filminstitut'
            ccb.address = 'Gothersgade 55, DK-1123 Copenhagen K, Denmark'
            ccb.phone = '+45 33743400'
            ccb.fax = '+45 33743403'
            ccb.email = 'dfi@dfi.dk'
            ccb.website = 'www.dfi.dk'
            ccb.save()
            log.info("Provider DFI successfully created")

        try:
            Provider.nodes.get(identifier='DIF')
            log.debug("Provider DIF already exists")
        except Provider.DoesNotExist:
            ccb = Provider()
            ccb.identifier = 'DIF'
            ccb.scheme = 'ACRO'
            ccb.name = 'Deutsches Filminstitut'
            ccb.address = 'Schaumainkai 41, 60596 Frankfurt am Main, Germany'
            ccb.phone = '+49 69 961220 403'
            ccb.fax = '+49 69 961220 999'
            ccb.email = 'richter@deutsches-filminstitut.de'
            ccb.website = 'www.deutsches-filminstitut.de'
            ccb.save()
            log.info("Provider DIF successfully created")

        try:
            Provider.nodes.get(identifier='OFM')
            log.debug("Provider OFM already exists")
        except Provider.DoesNotExist:
            ccb = Provider()
            ccb.identifier = 'OFM'
            ccb.scheme = 'ACRO'
            ccb.name = 'Österreichisches Filmmuseum'
            ccb.address = 'Augustinerstraße 1, 1010 Vienna, Austria'
            ccb.phone = '+43 1 533 70 54'
            ccb.fax = '+43 1 533 70 54 25'
            ccb.website = 'www.filmmuseum.at'
            ccb.save()
            log.info("Provider OFM successfully created")

        try:
            Provider.nodes.get(identifier='FDC')
            log.debug("Provider FDC already exists")
        except Provider.DoesNotExist:
            ccb = Provider()
            ccb.identifier = 'FDC'
            ccb.scheme = 'ACRO'
            ccb.name = 'Filmoteca de Catalunya'
            ccb.address = 'Plaça Salvador Seguí, 1 – 9, 08001 Barcelona, Spain'
            ccb.phone = '+34 935 671 070'
            ccb.website = 'www.filmoteca.cat'
            ccb.save()
            log.info("Provider FDC successfully created")

        try:
            Provider.nodes.get(identifier='MNC')
            log.debug("Provider MNC already exists")
        except Provider.DoesNotExist:
            ccb = Provider()
            ccb.identifier = 'MNC'
            ccb.scheme = 'ACRO'
            ccb.name = 'Museo Nazionale del Cinema'
            ccb.address = 'Via Montebello, 20 10124 Torino, Italia'
            ccb.phone = '+39 011.8138.580'
            ccb.fax = '+39 011 8138 585'
            ccb.email = 'cineteca@museocinema.it'
            ccb.website = 'http://www.museocinema.it'
            ccb.save()
            log.info("Provider MNC successfully created")


class Customizer(object):

    def custom_user_properties(self, properties):
        return properties
