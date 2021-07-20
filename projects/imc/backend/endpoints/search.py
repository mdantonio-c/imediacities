"""
Search endpoint

@author: Giuseppe Trotta <g.trotta@cineca.it>
"""
from typing import Any, Dict, Union

from imc.endpoints import IMCEndpoint
from imc.models import SearchCriteria, codelists
from restapi import decorators
from restapi.config import get_backend_url
from restapi.connectors import neo4j
from restapi.exceptions import BadRequest, Forbidden, NotFound, ServerError
from restapi.utilities.logs import log


class Search(IMCEndpoint):

    labels = ["file"]

    # allowed_term_fields = ("title", "description", "keyword", "contributor")
    # allowed_anno_types = ("TAG", "DSC", "LNK")

    @decorators.auth.optional()
    @decorators.get_pagination
    @decorators.use_kwargs(SearchCriteria)
    @decorators.endpoint(
        path="/search",
        summary="Search some videos",
        description="Search videos previously staged in the area.",
        responses={200: "A list of videos matching search criteria."},
    )
    def post(
        self, match, filtering, get_total, page, size, sort_by, sort_order, input_filter
    ):

        self.graph = neo4j.get_instance()

        user = self.get_user()
        page -= 1
        log.debug("paging: offset {}, limit {}", page, size)

        # check request for term matching
        provider = None

        # TODO: no longer used, to be removed
        multi_match_query = ""

        # check request for filtering
        filters = []
        # add filter for processed content with COMPLETE status
        filters.append(
            "MATCH (n)<-[:CREATION]-(:Item)-[:CONTENT_SOURCE]->(content:ContentStage) "
            + "WHERE content.status = 'COMPLETED'"
        )
        entity = "Creation"
        if filtering is not None:
            # check item type
            item_type = filtering.get("type")

            if item_type == "all":
                entity = "Creation"
            elif item_type == "video":
                entity = "AVEntity"
            elif item_type in ["image", "3d-model"]:
                entity = "NonAVEntity"
                filters.append(f"MATCH (n) WHERE n.non_av_type = '{item_type}'")
            else:
                # should never be reached
                raise ServerError("Unexpected item type")
            # PROVIDER
            provider = filtering.get("provider")
            log.debug("provider {0}", provider)
            # if provider is not None:
            #    filters.append(
            #        "MATCH (n)-[:RECORD_SOURCE]->(:RecordSource)-[:PROVIDED_BY]->(p:Provider)" +
            #        " WHERE p.identifier='{provider}'".format(provider=provider.strip()))
            # CITY
            city = filtering.get("city")
            if city is not None:
                filters.append(
                    "MATCH (n)-[:RECORD_SOURCE]->(:RecordSource)-[:PROVIDED_BY]->(p:Provider)"
                    + f" WHERE p.city='{city.strip()}'"
                )
            log.debug("city {}", city)
            # COUNTRY
            country = filtering.get("country")
            if country is not None:
                country = country.strip().upper()
                if codelists.fromCode(country, codelists.COUNTRY) is None:
                    raise NotFound(f"Invalid country code for: {country}")
                filters.append(
                    "MATCH (n)-[:COUNTRY_OF_REFERENCE]->(c:Country) WHERE c.code='{country_ref}'".format(
                        country_ref=country
                    )
                )
            # IPR STATUS
            if iprstatus := filtering.get("iprstatus"):
                if codelists.fromCode(iprstatus, codelists.RIGHTS_STATUS) is None:
                    raise NotFound(f"Invalid IPR status code for: {iprstatus}")
                filters.append(
                    "MATCH (n) WHERE n.rights_status = '{iprstatus}'".format(
                        iprstatus=iprstatus
                    )
                )
            # PRODUCTION YEAR RANGE
            missing_date = filtering.get("missingDate")
            if not missing_date:
                year_from = filtering.get("yearfrom")
                year_to = filtering.get("yearto")
                if year_from is not None or year_to is not None:
                    # set defaults if year is missing
                    year_from = "1890" if year_from is None else str(year_from)
                    year_to = "1999" if year_to is None else str(year_to)
                    # FIXME: this DO NOT work with image
                    date_clauses = []
                    if item_type == "video" or item_type == "all":
                        date_clauses.append(
                            "ANY(item in n.production_years where item >= '{yfrom}') "
                            "and ANY(item in n.production_years where item <= '{yto}')".format(
                                yfrom=year_from, yto=year_to
                            )
                        )
                    if item_type == "image" or item_type == "all":
                        date_clauses.append(
                            "ANY(item in n.date_created where substring(item, 0, 4) >= '{yfrom}') "
                            "and ANY(item in n.date_created where substring(item, 0 , 4) <= '{yto}')".format(
                                yfrom=year_from, yto=year_to
                            )
                        )
                    filters.append(
                        "MATCH (n) WHERE {clauses}".format(
                            clauses=" or ".join(date_clauses)
                        )
                    )
            # TERMS
            terms = filtering.get("terms")
            if terms:
                term_clauses = []
                iris = [
                    term["iri"]
                    for term in terms
                    if "iri" in term and term["iri"] is not None
                ]
                if iris:
                    term_clauses.append(f"body.iri IN {iris}")
                free_terms = [
                    term["label"]
                    for term in terms
                    if "iri" not in term or term["iri"] is None and "label" in term
                ]
                if free_terms:
                    term_clauses.append(f"body.value IN {free_terms}")
                if term_clauses:
                    filters.append(
                        "MATCH (n)<-[:CREATION]-(i:Item)<-[:SOURCE]-(tag:Annotation {{annotation_type:'TAG'}})-[:HAS_BODY]-(body) "
                        "WHERE {clauses}".format(clauses=" or ".join(term_clauses))
                    )
            # ANNOTATED BY
            annotated_by = filtering.get("annotated_by")
            # if no user ignore this filter
            if user and annotated_by:
                # only annotated *BY ME* is autorized (except for the admin)
                anno_user_id = annotated_by.get("user")
                iamadmin = self.auth.is_admin(user)
                if user.uuid != anno_user_id and not iamadmin:
                    raise Forbidden(
                        "You are not allowed to search for item that are not annotated by you",
                    )
                if iamadmin:
                    # check if 'user' in annotated_by filter exists
                    try:
                        v = self.graph.User.nodes.get(uuid=anno_user_id)
                    except self.graph.User.DoesNotExist:
                        log.debug("User with uuid {} does not exist", anno_user_id)
                        raise NotFound(
                            "Please specify a valid user id in annotated_by filter"
                        )
                anno_type = annotated_by.get("type", "TAG")
                filters.append(
                    "MATCH (n)<-[:CREATION]-(i:Item)<-[:SOURCE]-(tag:Annotation {{annotation_type:'{type}'}})"
                    "-[IS_ANNOTATED_BY]->(:User {{uuid:'{user}'}})".format(
                        user=anno_user_id, type=anno_type
                    )
                )

        fulltext = None
        if (
            match is not None
            and (term := self.graph.sanitize_input(match.get("term"))) != ""
        ):
            term = self.graph.fuzzy_tokenize(term)
            fields = match.get("fields", ["Title"])
            term_fields = "|".join(list(map((lambda x: f"has_{x}"), fields))).upper()
            log.debug("full-text search in fields {}. Term: {}", fields, term)

            # Create with:
            # CALL db.index.fulltext.createNodeIndex("titles",["Title", "Description", "Keyword"],["text", "term"])

            fulltext = """
                CALL db.index.fulltext.queryNodes("titles", '{term}')
                YIELD node, score
                WITH node, score
                MATCH (n:{entity})-[:{fields}]->(node)
            """.format(
                term=term, entity=entity, fields=term_fields
            )
            # RETURN node, n, score

        # first request to get the number of elements to be returned
        if fulltext is not None:
            countv = "{fulltext} {filters} RETURN COUNT(DISTINCT(n))".format(
                fulltext=fulltext, filters=" ".join(filters)
            )
            query = (
                "{fulltext} {filters} "
                "RETURN DISTINCT(n) SKIP {offset} LIMIT {limit}".format(
                    fulltext=fulltext,
                    filters=" ".join(filters),
                    offset=page * size,
                    limit=size,
                )
            )

        else:
            countv = (
                "MATCH (n:{entity})"
                " {filters} "
                " {match} "
                " RETURN COUNT(DISTINCT(n))".format(
                    entity=entity, filters=" ".join(filters), match=multi_match_query
                )
            )
            query = (
                "MATCH (n:{entity})"
                " {filters} "
                " {match} "
                "RETURN DISTINCT(n) SKIP {offset} LIMIT {limit}".format(
                    entity=entity,
                    filters=" ".join(filters),
                    match=multi_match_query,
                    offset=page * size,
                    limit=size,
                )
            )

        data = []
        meta_response: Dict[str, Union[int, Dict[Any, Any]]] = {
            "totalItems": 0,
            "countByProviders": 0,
            "countByYears": 0,
        }
        # get total number of elements
        try:
            numels = [row[0] for row in self.graph.cypher(countv)][0]
        except BaseException as e:
            log.error(e)
            raise BadRequest("Invalid query parameters")

        log.debug("Number of elements retrieved: {}", numels)

        # return also the total number of elements
        meta_response["totalItems"] = numels
        # log.debug(query)

        result = self.graph.cypher(query)
        api_url = get_backend_url()
        for row in result:
            if "AVEntity" in row[0].labels:
                v = self.graph.AVEntity.inflate(row[0])
            elif "NonAVEntity" in row[0].labels:
                v = self.graph.NonAVEntity.inflate(row[0])
            else:
                # should never be reached
                raise ServerError("Unexpected item type")

            item = v.item.single()

            if isinstance(v, self.graph.AVEntity):
                # video
                video_url = api_url + "/api/videos/" + v.uuid
                video = self.getJsonResponse(
                    v,
                    max_relationship_depth=1,
                    relationships_expansion=[
                        "record_sources.provider",
                        "item.ownership",
                        "item.revision",
                    ],
                )
                video["links"] = {}
                video["links"]["content"] = video_url + "/content?type=video"
                if item.thumbnail is not None:
                    video["links"]["thumbnail"] = video_url + "/content?type=thumbnail"
                video["links"]["summary"] = video_url + "/content?type=summary"
                data.append(video)
            elif isinstance(v, self.graph.NonAVEntity):
                # image
                image_url = api_url + "/api/images/" + v.uuid
                image = self.getJsonResponse(
                    v,
                    max_relationship_depth=1,
                    relationships_expansion=[
                        "record_sources.provider",
                        "item.ownership",
                        # 'titles.creation',
                        # 'keywords.creation',
                        # 'descriptions.creation',
                    ],
                )
                image["links"] = {}
                image["links"]["content"] = image_url + "/content?type=image"
                if item.thumbnail is not None:
                    image["links"]["thumbnail"] = image_url + "/content?type=thumbnail"
                image["links"]["summary"] = image_url + "/content?type=summary"
                data.append(image)

        # count result by provider if provider == null
        if provider is None:
            count_by_provider_query = (
                "MATCH (n:{entity})"
                " {filters} "
                " {match} "
                "MATCH (n)-[:RECORD_SOURCE]->(r:RecordSource)-[:PROVIDED_BY]->(p:Provider) "
                "WITH distinct p, count(distinct n) as numberOfCreations "
                "RETURN p.identifier, numberOfCreations".format(
                    entity=entity, filters=" ".join(filters), match=multi_match_query
                )
            )
            # log.debug(count_by_provider_query)
            result_p_count = self.graph.cypher(count_by_provider_query)
            group_by_providers = {}
            for row in result_p_count:
                group_by_providers[row[0]] = row[1]
            # log.debug(group_by_providers)
            meta_response["countByProviders"] = group_by_providers

        # count result by year
        count_by_year_query = (
            "MATCH (n:{entity})"
            " {filters} "
            " {match} "
            "WITH distinct n WITH collect(substring(head(n.production_years), 0, 3)) + collect(substring(head(n.date_created), 0, 3)) as years "
            "UNWIND years as row "
            "RETURN row + '0' as decade, count(row) as count order by decade".format(
                entity=entity, filters=" ".join(filters), match=multi_match_query
            )
        )
        # log.debug(count_by_year_query)
        result_y_count = self.graph.cypher(count_by_year_query)
        group_by_years = {}
        for row in result_y_count:
            group_by_years[row[0]] = row[1]
        meta_response["countByYears"] = group_by_years

        resp = {"data": data, "meta": meta_response}

        return self.response(resp)
