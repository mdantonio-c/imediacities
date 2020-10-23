from restapi.customizer import BaseCustomizer
from restapi.models import fields, validate
from restapi.services.authentication import Role
from restapi.utilities.logs import log


class Initializer:
    def __init__(self, services, app=None):

        neo4j = services["neo4j"]

        try:
            neo4j.Role.nodes.get(name=Role.LOCAL_ADMIN.value)
            log.debug("Coordinator neo4j.Role already exists")
        except neo4j.Role.DoesNotExist:
            local_admin = neo4j.Role()
            local_admin.name = Role.LOCAL_ADMIN.value
            local_admin.description = "Coordinator"
            local_admin.save()
            log.info("Coordinator neo4j.Role successfully created")

        try:
            neo4j.Role.nodes.get(name="Archive")
            log.debug("Archive neo4j.Role already exists")
        except neo4j.Role.DoesNotExist:
            archiver = neo4j.Role()
            archiver.name = "Archive"
            archiver.description = "Archive"
            archiver.save()
            log.info("Archive neo4j.Role successfully created")

        try:
            neo4j.Role.nodes.get(name="Researcher")
            log.debug("Researcher neo4j.Role already exists")
        except neo4j.Role.DoesNotExist:
            researcher = neo4j.Role()
            researcher.name = "Researcher"
            researcher.description = "Researcher"
            researcher.save()
            log.info("Researcher neo4j.Role successfully created")

        try:
            neo4j.Role.nodes.get(name="Reviser")
            log.debug("Reviser neo4j.Role already exists")
        except neo4j.Role.DoesNotExist:
            reviser = neo4j.Role()
            reviser.name = "Reviser"
            reviser.description = "Reviser"
            reviser.save()
            log.info("Reviser neo4j.Role successfully created")

        try:
            admin = neo4j.Role.nodes.get(name="admin_root")
            admin.description = "Admin"
            admin.save()
            log.info("Admin neo4j.Role successfully updated")
        except neo4j.Role.DoesNotExist:
            log.warning("Admin neo4j.Role does not exist")

        if len(neo4j.Group.nodes) > 0:
            log.info("Found one or more already defined groups")
        else:
            log.warning("No group defined")
            group = neo4j.Group()
            group.fullname = "test"
            group.shortname = "test"
            group.save()

            group = neo4j.Group()
            group.fullname = "Default user group"
            group.shortname = "default"
            group.save()

            log.info("Groups successfully created")

        # Providers
        try:
            neo4j.Provider.nodes.get(identifier="CCB")
            log.debug("Provider CCB already exists")
        except neo4j.Provider.DoesNotExist:
            ccb = neo4j.Provider()
            ccb.identifier = "CCB"
            ccb.scheme = "ACRO"
            ccb.name = "Fondazione Cineteca di Bologna"
            ccb.city = "Bologna"
            ccb.address = "Via Riva di Reno, 72, 40122 Bologna BO, Italy"
            ccb.phone = "+39 (0) 512194820"
            ccb.fax = "+39 (0) 512194821"
            ccb.email = "cinetecadirezione@cineteca.bologna.it"
            ccb.website = "www.cinetecadibologna.it"
            ccb.save()
            log.info("Provider CCB successfully created")

        try:
            neo4j.Provider.nodes.get(identifier="TTE")
            log.debug("Provider TTE already exists")
        except neo4j.Provider.DoesNotExist:
            tte = neo4j.Provider()
            tte.identifier = "TTE"
            tte.scheme = "ACRO"
            tte.name = "Tainiothiki tis Ellados"
            tte.city = "Athens"
            tte.address = "Iera Odos 48 and Megalou Alexandrou 134-136 10435 Athens"
            tte.phone = "+30 210 3612046"
            tte.fax = "+39 210 3628468"
            tte.email = "nina@tainiothiki.gr"
            tte.website = "www.tainiothiki.gr"
            tte.save()
            log.info("Provider TTE successfully created")

        try:
            neo4j.Provider.nodes.get(identifier="CRB")
            log.debug("Provider CRB already exists")
        except neo4j.Provider.DoesNotExist:
            crb = neo4j.Provider()
            crb.identifier = "CRB"
            crb.scheme = "ACRO"
            crb.name = "Cinémathèque Royale de Belgique"
            crb.city = "Brussels"
            crb.address = "Rue Ravenstein 3, 1000 Bruxelles, Belgium"
            crb.phone = "+32 (0) 25511900"
            crb.fax = "+32 (0) 25511907"
            crb.email = "info@cinematek.be"
            crb.website = "www.cinematek.be"
            crb.save()
            log.info("Provider CRB successfully created")

        try:
            neo4j.Provider.nodes.get(identifier="SFI")
            log.debug("Provider SFI already exists")
        except neo4j.Provider.DoesNotExist:
            sfi = neo4j.Provider()
            sfi.identifier = "SFI"
            sfi.scheme = "ACRO"
            sfi.name = "Svenska Filminstitutet"
            sfi.city = "Stockholm"
            sfi.address = "Box 27 126, 102 52 Stockholm, Sweden"
            sfi.phone = "08-665 11 00"
            sfi.email = "filmarkivet.se@filminstitutet.se"
            sfi.website = "www.filminstitutet.se"
            sfi.save()
            log.info("Provider SFI successfully created")

        try:
            neo4j.Provider.nodes.get(identifier="DFI")
            log.debug("Provider DFI already exists")
        except neo4j.Provider.DoesNotExist:
            dfi = neo4j.Provider()
            dfi.identifier = "DFI"
            dfi.scheme = "ACRO"
            dfi.name = "Det Danske Filminstitut"
            dfi.city = "Copenhagen"
            dfi.address = "Gothersgade 55, DK-1123 Copenhagen K, Denmark"
            dfi.phone = "+45 33743400"
            dfi.fax = "+45 33743403"
            dfi.email = "dfi@dfi.dk"
            dfi.website = "www.dfi.dk"
            dfi.save()
            log.info("Provider DFI successfully created")

        try:
            neo4j.Provider.nodes.get(identifier="DIF")
            log.debug("Provider DIF already exists")
        except neo4j.Provider.DoesNotExist:
            dif = neo4j.Provider()
            dif.identifier = "DIF"
            dif.scheme = "ACRO"
            dif.name = "Deutsches Filminstitut"
            dif.city = "Frankfurt"
            dif.address = "Schaumainkai 41, 60596 Frankfurt am Main, Germany"
            dif.phone = "+49 69 961220 403"
            dif.fax = "+49 69 961220 999"
            dif.email = "richter@deutsches-filminstitut.de"
            dif.website = "www.deutsches-filminstitut.de"
            dif.save()
            log.info("Provider DIF successfully created")

        try:
            neo4j.Provider.nodes.get(identifier="OFM")
            log.debug("Provider OFM already exists")
        except neo4j.Provider.DoesNotExist:
            ofm = neo4j.Provider()
            ofm.identifier = "OFM"
            ofm.scheme = "ACRO"
            ofm.name = "Österreichisches Filmmuseum"
            ofm.city = "Vienna"
            ofm.address = "Augustinerstraße 1, 1010 Vienna, Austria"
            ofm.phone = "+43 1 533 70 54"
            ofm.fax = "+43 1 533 70 54 25"
            ofm.website = "www.filmmuseum.at"
            ofm.save()
            log.info("Provider OFM successfully created")

        try:
            neo4j.Provider.nodes.get(identifier="WSTLA")
            log.debug("Provider WSTLA already exists")
        except neo4j.Provider.DoesNotExist:
            ofm = neo4j.Provider()
            ofm.identifier = "WSTLA"
            ofm.scheme = "ACRO"
            ofm.name = "Wiener Stadt- und Landesarchiv"
            ofm.city = "Vienna"
            ofm.address = "Gasometer D | Guglgasse 14, A-1110 Wien, Austria"
            ofm.phone = "+43 1 4000 84808 | +43 1 4000 84819"
            ofm.fax = "+43 1 4000 84809"
            ofm.email = "post@ma08.wien.gv.at"
            ofm.save()
            log.info("Provider OFM successfully created")

        try:
            neo4j.Provider.nodes.get(identifier="FDC")
            log.debug("Provider FDC already exists")
        except neo4j.Provider.DoesNotExist:
            fdc = neo4j.Provider()
            fdc.identifier = "FDC"
            fdc.scheme = "ACRO"
            fdc.name = "Filmoteca de Catalunya"
            fdc.city = "Barcelona"
            fdc.address = "Plaça Salvador Seguí, 1 – 9, 08001 Barcelona, Spain"
            fdc.phone = "+34 935 671 070"
            fdc.website = "www.filmoteca.cat"
            fdc.save()
            log.info("Provider FDC successfully created")

        try:
            neo4j.Provider.nodes.get(identifier="MNC")
            log.debug("Provider MNC already exists")
        except neo4j.Provider.DoesNotExist:
            mnc = neo4j.Provider()
            mnc.identifier = "MNC"
            mnc.scheme = "ACRO"
            mnc.name = "Museo Nazionale del Cinema"
            mnc.city = "Turin"
            mnc.address = "Via Montebello, 20 10124 Torino, Italia"
            mnc.phone = "+39 011.8138.580"
            mnc.fax = "+39 011 8138 585"
            mnc.email = "cineteca@museocinema.it"
            mnc.website = "http://www.museocinema.it"
            mnc.save()
            log.info("Provider MNC successfully created")


class Customizer(BaseCustomizer):
    @staticmethod
    def custom_user_properties_pre(properties):
        extra_properties = {}
        # if 'myfield' in properties:
        #     extra_properties['myfield'] = properties['myfield']
        return properties, extra_properties

    @staticmethod
    def custom_user_properties_post(user, properties, extra_properties, db):

        try:
            group = db.Group.nodes.get(shortname="default")
        except db.Group.DoesNotExist:
            log.warning("Unable to find default group, creating")
            group = db.Group()
            group.fullname = "Default user group"
            group.shortname = "default"
            group.save()

        log.info("Link {} to group {}", user.email, group.shortname)
        user.belongs_to.connect(group)

        return True

    @staticmethod
    def manipulate_profile(ref, user, data):
        data["declared_institution"] = user.declared_institution

        return data

    @staticmethod
    def get_user_editable_fields(request):
        return {}

    @staticmethod
    def get_custom_input_fields(request):

        # required = request and request.method == "POST"
        return {
            "declared_institution": fields.Str(
                required=False,
                default="none",
                validate=validate.OneOf(
                    choices=["archive", "university", "research_institution", "none"],
                    labels=[
                        "Archive",
                        "University",
                        "Research Institution",
                        "None of the above",
                    ],
                ),
            )
        }

    @staticmethod
    def get_custom_output_fields(request):
        fields = Customizer.get_custom_input_fields(request)

        return fields
