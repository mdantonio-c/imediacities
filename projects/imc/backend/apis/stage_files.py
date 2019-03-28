# -*- coding: utf-8 -*-

"""
List content from upload dir and import of data and metadata
"""
import os
from utilities.logs import get_logger
from restapi import decorators as decorate
from restapi.services.neo4j.graph_endpoints import GraphBaseOperations
from restapi.exceptions import RestApiException
from restapi.services.neo4j.graph_endpoints import catch_graph_exceptions
from utilities import htmlcodes as hcodes

from imc.tasks.services.efg_xmlparser import EFG_XMLParser

from restapi.flask_ext.flask_celery import CeleryExt

log = get_logger(__name__)


#####################################
class Stage(GraphBaseOperations):

    allowed_import_mode = ('clean', 'fast', 'skip')

    def getType(self, filename):
        name, file_extension = os.path.splitext(filename)

        if file_extension is None:
            return "unknown"

        metadata_exts = ['.xml', '.xls']
        if file_extension in metadata_exts:
            return "metadata"

        video_exts = ['.mp4', '.ts', '.mpg', '.mpeg', '.mkv']
        if file_extension in video_exts:
            return "video"

        audio_exts = ['.aac', '.mp2', '.mp3', '.wav']
        if file_extension in audio_exts:
            return "audio"

        image_exts = ['.tif', '.jpg', '.tiff', '.jpeg']
        if file_extension in image_exts:
            return "image"

        text_exts = ['.pdf', '.doc', '.docx']
        if file_extension in text_exts:
            return "text"

        return "unknown"

    def lookup_content(self, path, source_id):
        '''
        Look for a filename in the form of:
        ARCHIVE_SOURCEID.[extension]
        '''
        content_filename = None
        files = [f for f in os.listdir(path) if not f.endswith('.xml')]
        for f in files:
            tokens = os.path.splitext(f)[0].split('_')
            if len(tokens) == 0:
                continue
            if tokens[-1] == source_id:
                log.info('Content file FOUND: {0}'.format(f))
                # content_path = os.path.join(path, f)
                content_filename = f
                break
        return content_filename

    def extract_creation_ref(self, path):
        """
        Extract the source id reference from the XML file
        """
        parser = EFG_XMLParser()
        return parser.get_creation_ref(path)

    @decorate.catch_error()
    @catch_graph_exceptions
    def head(self, group=None):
        self.graph = self.get_service_instance('neo4j')

        if not self.auth.verify_admin():
            # Only admins can specify a different group to be inspected
            group = None

        if group is None:
            group = self.getSingleLinkedNode(
                self.get_current_user().belongs_to)
        else:
            group = self.graph.Group.nodes.get_or_none(uuid=group)

        if group is None:
            return 0

        upload_dir = os.path.join("/uploads", group.uuid)
        if not os.path.exists(upload_dir):
            return 0

        counter = 0
        for f in os.listdir(upload_dir):

            path = os.path.join(upload_dir, f)
            if not os.path.isfile(path):
                continue
            if f[0] == '.':
                continue

            counter += 1

        return counter

    @decorate.catch_error()
    @catch_graph_exceptions
    def get(self, group=None):

        self.graph = self.get_service_instance('neo4j')

        if not self.auth.verify_admin():
            # Only admins can specify a different group to be inspected
            group = None

        if group is None:
            group = self.getSingleLinkedNode(
                self.get_current_user().belongs_to)
        else:
            group = self.graph.Group.nodes.get_or_none(uuid=group)

        if group is None:
            raise RestApiException(
                "No group defined for this user",
                status_code=hcodes.HTTP_BAD_REQUEST)

        upload_dir = os.path.join("/uploads", group.uuid)
        if not os.path.exists(upload_dir):
            os.mkdir(upload_dir)
            if not os.path.exists(upload_dir):
                return self.force_response(
                    [], errors=["Upload dir not found"])

        data = []

        params = self.get_input()
        get_total = params.get('get_total', False)
        if not get_total:
            current_page, limit = self.get_paging()
            offset = (current_page - 1) * limit

        counter = 0
        for f in os.listdir(upload_dir):

            path = os.path.join(upload_dir, f)
            if not os.path.isfile(path):
                continue
            if f[0] == '.':
                continue

            counter += 1

            if get_total:
                continue

            if offset >= counter:
                continue

            if offset + limit < counter:
                break

            stat = os.stat(path)

            row = {}
            row['name'] = f
            row['size'] = stat.st_size
            row['creation'] = stat.st_ctime
            row['modification'] = stat.st_mtime
            row['type'] = self.getType(f)
            row['status'] = "-"
            res = self.graph.Stage.nodes.get_or_none(filename=f)
            if res is not None:
                row['status'] = res.status
                row['status_message'] = res.status_message
                row['task_id'] = res.task_id
                row['warnings'] = res.warnings
                # cast down to Meta or Content stage
                subres = res.downcast()
                if 'MetaStage' in subres.labels():
                    item = subres.item.single()
                    # add binding info ONLY for processed record
                    if item is not None:
                        binding = {}
                        source_id = None
                        creation = item.creation.single()
                        if creation is not None:
                            sources = creation.record_sources.all()
                            source_id = sources[0].source_id
                            binding['source_id'] = source_id
                        content_stage = item.content_source.single()
                        if content_stage is not None:
                            binding['filename'] = content_stage.filename
                            binding['status'] = content_stage.status
                        else:
                            binding['filename'] = self.lookup_content(
                                upload_dir, source_id)
                            binding['status'] = 'PENDING'
                        row['binding'] = binding

            data.append(row)

        if get_total:
            return {"total": counter}

        return self.force_response(data)

    @decorate.catch_error()
    @catch_graph_exceptions
    def post(self):
        """
        Start IMPORT
        1) estraggo il source id dal file dei metadati
            se non lo trovo -> RestApiException
        2) cerco nel database se esiste già un META_STAGE collegato a quel SOURCE_ID e appartenente al gruppo
            se ne trovo più di uno -> RestApiException
            se ne trovo uno -> updating metadata
                se il nome del file dei metadati è diverso da quello in db -> RestApiException
                cerco se c'è un content stage associato a quel meta stage
                    se esiste e se ha status COMPLETED -> mode=skip
            se ne trovo zero -> creating new element
                se il file dei metadati non rispetta la convenzione del name '<archive code>_<source id>.xml'
                    cambio il nome al file
                cerco se esiste già un metastage con quel filename
                    se non esiste lo creo
        3) faccio partire l'import con parametri: path, meta_stage.uuid, mode, metadata_update
        """

        self.graph = self.get_service_instance('neo4j')

        group = self.getSingleLinkedNode(self.get_current_user().belongs_to)

        if group is None:
            raise RestApiException(
                "No group defined for this user",
                status_code=hcodes.HTTP_BAD_REQUEST)

        upload_dir = os.path.join("/uploads", group.uuid)
        if not os.path.exists(upload_dir):
            raise RestApiException(
                "Upload dir not found",
                status_code=hcodes.HTTP_BAD_REQUEST)

        input_parameters = self.get_input()

        if 'filename' not in input_parameters:
            raise RestApiException(
                "Filename not found",
                status_code=hcodes.HTTP_BAD_REQUEST)

        filename = input_parameters['filename']
        force_reprocessing = input_parameters.get('force_reprocessing', False)
        mode = input_parameters.get('mode', 'clean').strip().lower()
        if mode not in self.__class__.allowed_import_mode:
            raise RestApiException(
                "Bad mode parameter: expected one of %s" %
                (self.__class__.allowed_import_mode, ),
                status_code=hcodes.HTTP_BAD_REQUEST)

        path = os.path.join(upload_dir, filename)
        if not os.path.isfile(path):
            raise RestApiException(
                "File not found: %s" % filename,
                status_code=hcodes.HTTP_BAD_REQUEST)

        # 1) estraggo il source id dal file dei metadati
        log.debug("Extracting source id from metadata file %s", filename)
        source_id = self.extract_creation_ref(path)
        if source_id is None:
            log.debug("No source ID found in metadata file %s", path)
            raise RestApiException(
                "No source ID found in metadata file: %s" % filename,
                status_code=hcodes.HTTP_BAD_CONFLICT)
        log.debug("Source id %s found in metadata file", source_id)

        # 2) cerco nel database se esiste già un META_STAGE collegato a quel SOURCE_ID
        #     e appartenente al gruppo
        meta_stage = None
        try:
            query = "match (g:Group)<-[r4:IS_OWNED_BY]-(ms:MetaStage) \
                        match (ms:MetaStage)<-[r3:META_SOURCE]-(i:Item) \
                        match (i:Item)-[r2:CREATION]->(c:Creation) \
                        match (c:Creation)-[r1:RECORD_SOURCE]-> (rs:RecordSource) \
                        WHERE rs.source_id = '{source_id}' and g.uuid = '{guuid}' \
                        return ms"

            results = self.graph.cypher(query.format(
                source_id=source_id, guuid=group.uuid))
            c = [self.graph.MetaStage.inflate(row[0]) for row in results]
            if len(c) > 1:
                # there are more than one MetaStage related to the same source id: Database incoherence!
                log.errors(
                    "Database incoherence: there are more than one MetaStage related to the same source id %s" % source_id)
                raise RestApiException(
                    "System incoherent state: it is not possible to perform the import",
                    status_code=hcodes.HTTP_BAD_CONFLICT)
            if len(c) == 1:
                # Source id already exists in database: updating metadata
                log.debug("Source id %s already exists in database" %
                          source_id)
                meta_stage = c[0]
                if meta_stage is not None:
                    dbFilename = meta_stage.filename
                    log.debug("dbFilename=%s" % dbFilename)
                    if filename != dbFilename:
                        raise RestApiException(
                            "Source id %s already esists in database but with different filename %s: cannot proceed with import!" % (
                                source_id, dbFilename),
                            status_code=hcodes.HTTP_BAD_CONFLICT)

                    # cerco se c'è un content stage associato a quel meta stage per vedere se status COMPLETED
                    query2 = "MATCH (cs:ContentStage)<-[r1:CONTENT_SOURCE]-(i:Item) " \
                             "MATCH (i)-[r2:META_SOURCE]-> (ms:MetaStage) " \
                             "WHERE ms.uuid='{uuid}' " \
                             "RETURN cs"
                    results2 = self.graph.cypher(
                        query2.format(uuid=meta_stage.uuid))
                    c2 = [self.graph.ContentStage.inflate(
                        row[0]) for row in results2]
                    if len(c2) == 1:
                        content_stage = c2[0]
                        if content_stage is not None and content_stage.status == 'COMPLETED' and not force_reprocessing:
                            log.warn("This content item has already been "
                                     "successfully processed. Force SKIP mode.")
                            mode = 'skip'
                else:
                    log.debug("meta_stage is null")
                    raise RestApiException(
                        "System incoherence error: it is not possible to perform the import",
                        status_code=hcodes.HTTP_BAD_CONFLICT)
            if len(c) == 0:
                # Source id does not exist in database: creating new element
                log.debug(
                    "Source id %s does not exist in database: creating new element" % source_id)
                # forziamo la convenzione del filename '<archive code>_<source id>.xml'
                standard_filename = group.shortname + '_' + source_id + '.xml'
                if filename != standard_filename:
                    log.debug("File %s has not standard file name: renaming it to standard %s" % (
                        filename, standard_filename))
                    standard_path = os.path.join(upload_dir, standard_filename)
                    # rinomino il file nel filesystem
                    try:
                        # cambio il nome al file dell'utente
                        # TODO come faccio ad avvisarlo????
                        os.replace(path, standard_path)
                    except OSError as ose:
                        log.debug("Error in renaming file %s to %s: " %
                                  (path, standard_path))
                        raise RestApiException(
                            "System error: cannot rename file %s" % path,
                            status_code=hcodes.HTTP_BAD_CONFLICT)

                    path = standard_path

                # cerco se esiste già un metastage con quel filename altrimenti lo creo
                properties = {}
                properties['filename'] = standard_filename
                properties['path'] = path
                try:
                    meta_stage = self.graph.MetaStage.nodes.get(**properties)
                    log.debug("MetaStage already exists for file %s, meta_stage.uuid=%s" % (
                        path, meta_stage.uuid))
                except self.graph.MetaStage.DoesNotExist:
                    log.debug("MetaStage does not exists for file %s" % path)
                    meta_stage = self.graph.MetaStage(**properties).save()
                    meta_stage.ownership.connect(group)
                    log.debug("MetaStage created for %s, meta_stage.uuid=%s" % (
                        path, meta_stage.uuid))

            metadata_update = input_parameters.get('update', True)

            log.debug("Starting import of file path=%s" % (path))
            log.debug("with meta_stage.uuid=%s" % (meta_stage.uuid))
            log.debug("with mode=%s" % (mode))
            log.debug("with metadata_update=%s" % (metadata_update))

        except self.graph.MetaStage.DoesNotExist:
            log.debug("MetaStage not exist for source id %s " % source_id)

        # 3) starting import
        task = CeleryExt.import_file.apply_async(
            args=[path, meta_stage.uuid, mode, metadata_update],
            countdown=10
        )

        meta_stage.status = "IMPORTING"
        meta_stage.task_id = task.id
        meta_stage.save()

        return self.force_response(task.id)

    @decorate.catch_error()
    @catch_graph_exceptions
    def delete(self, filename):

        self.graph = self.get_service_instance('neo4j')

        group = self.getSingleLinkedNode(self.get_current_user().belongs_to)

        if group is None:
            raise RestApiException(
                "No group defined for this user",
                status_code=hcodes.HTTP_BAD_REQUEST)

        upload_dir = os.path.join("/uploads", group.uuid)
        if not os.path.exists(upload_dir):
            raise RestApiException(
                "Upload dir not found",
                status_code=hcodes.HTTP_BAD_REQUEST)

        input_parameters = self.get_input()

        # if 'filename' not in input_parameters:
        #     raise RestApiException(
        #         "Filename not found",
        #         status_code=hcodes.HTTP_BAD_REQUEST)

        # filename = input_parameters['filename']

        path = os.path.join(upload_dir, filename)
        if not os.path.isfile(path):
            raise RestApiException(
                "File not found: %s" % filename,
                status_code=hcodes.HTTP_BAD_REQUEST)

        os.remove(path)
        return self.empty_response()
