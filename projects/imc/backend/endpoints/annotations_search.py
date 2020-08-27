"""
Search endpoint for annotations
"""

from imc.endpoints import IMCEndpoint
from imc.models import AnnotationSearch, codelists
from restapi import decorators
from restapi.exceptions import BadRequest, RestApiException
from restapi.models import fields
from restapi.utilities.htmlcodes import hcodes


class SearchAnnotations(IMCEndpoint):
    @decorators.auth.require()
    @decorators.catch_graph_exceptions
    @decorators.use_kwargs(
        {"filtering": fields.Nested(AnnotationSearch, data_key="filter")}
    )
    @decorators.endpoint(
        path="/annotations/search",
        summary="Search for annotations",
        description="Search for annotations",
        responses={200: "A list of annotation matching search criteria."},
    )
    def post(self, filtering=None):

        self.graph = self.get_service_instance("neo4j")

        filters = []
        starters = []
        projections = []
        order_by = ""
        if filtering:
            anno_type = filtering.get("annotation_type")

            filters.append(f"WHERE anno.annotation_type='{anno_type}'")
            # add filter for processed content with COMPLETE status
            filters.append(
                "MATCH (creation:Creation)<-[:CREATION]-(:Item)-[:CONTENT_SOURCE]->(content:ContentStage) "
                + "WHERE content.status = 'COMPLETED' "
            )
            filters.append(
                "MATCH (title:Title)<-[:HAS_TITLE]-(creation)<-[:CREATION]-(i:Item)<-[:SOURCE]-(anno)"
            )
            projections.append(
                "collect(distinct creation{.*, type:i.item_type, titles }) AS creations"
            )
            if anno_type == "TAG":
                # look for geo distance filter
                geo_distance = filtering.get("geo_distance")
                if geo_distance is not None:
                    distance = geo_distance["distance"]
                    location = geo_distance["location"]
                    starters.append(
                        "WITH point({{longitude: {lon}, latitude: {lat} }}) as cityPosition, "
                        "{dist} as distanceInMeters".format(
                            lon=location["longitude"],
                            lat=location["latitude"],
                            dist=distance,
                        )
                    )
                    filters.append(
                        "MATCH (anno)-[:HAS_BODY]-(body:ResourceBody) "
                        "WHERE body.spatial IS NOT NULL AND "
                        "distance(cityPosition, point({latitude:body.spatial[0], longitude:body.spatial[1]})) < distanceInMeters"
                    )
                    projections.append(
                        "distance(cityPosition, point({longitude:body.spatial[0],latitude:body.spatial[1]})) as distance"
                    )
                    order_by = "ORDER BY distance"

            if creation := filtering.get("creation"):
                if c_match := creation.get("match"):
                    if term := c_match.get("term"):
                        term = self.graph.sanitize_input(term)
                    multi_match = []
                    multi_match_where = []
                    multi_match_query = ""

                    fields = c_match.get("fields")
                    if term is not None and (fields is None or len(fields) == 0):
                        raise BadRequest("Match term fields cannot be empty")
                    if fields is None:
                        fields = []

                    multi_match_fields = []
                    multi_optional_match = []
                    for f in fields:
                        if not term:
                            # catch '*'
                            break
                        if f == "title":
                            multi_match.append(
                                "MATCH (creation)-[:HAS_TITLE]->(t:Title)"
                            )
                            multi_match_fields.append("t")
                            multi_match_where.append(f"t.text =~ '(?i).*{term}.*'")
                        elif f == "description":
                            multi_match.append(
                                "OPTIONAL MATCH (creation)-[:HAS_DESCRIPTION]->(d:Description)"
                            )
                            multi_match_fields.append("d")
                            multi_match_where.append(f"d.text =~ '(?i).*{term}.*'")
                        elif f == "keyword":
                            multi_optional_match.append(
                                "OPTIONAL MATCH (creation)-[:HAS_KEYWORD]->(k:Keyword)"
                            )
                            multi_match_fields.append("k")
                            multi_match_where.append(f"k.term =~ '(?i){term}'")
                        elif f == "contributor":
                            multi_optional_match.append(
                                "OPTIONAL MATCH (creation)-[:CONTRIBUTED_BY]->(a:Agent)"
                            )
                            multi_match_fields.append("a")
                            multi_match_where.append(
                                "ANY(item in a.names where item =~ '(?i).*{term}.*')".format(
                                    term=term
                                )
                            )
                        else:
                            # should never be reached
                            raise RestApiException(
                                "Unexpected field type",
                                status_code=hcodes.HTTP_SERVER_ERROR,
                            )
                    if len(multi_match) > 0:
                        multi_match_query = (
                            " ".join(multi_match)
                            + " "
                            + " ".join(multi_optional_match)
                            + " WITH creation, cityPosition, title, i, body, "
                            + ", ".join(multi_match_fields)
                            + " WHERE "
                            + " OR ".join(multi_match_where)
                        )
                        filters.append(multi_match_query)

                c_filter = creation.get("filtering")
                # TYPE
                c_type = c_filter.get("type")

                if c_type != "all":
                    filters.append(
                        "MATCH (i) WHERE i.item_type =~ '(?i){c_type}'".format(
                            c_type=c_type
                        )
                    )
                # PROVIDER
                c_provider = c_filter.get("provider")
                if c_provider is not None:
                    filters.append(
                        "MATCH (creation)-[:RECORD_SOURCE]->(:RecordSource)-[:PROVIDED_BY]->(p:Provider)"
                        " WHERE p.identifier='{provider}'".format(
                            provider=c_provider.strip()
                        )
                    )
                # IPR STATUS
                if c_iprstatus := c_filter.get("iprstatus"):
                    if codelists.fromCode(c_iprstatus, codelists.RIGHTS_STATUS) is None:
                        raise RestApiException(
                            "Invalid IPR status code for: " + c_iprstatus
                        )
                    filters.append(
                        "MATCH (creation) WHERE creation.rights_status = '{iprstatus}'".format(
                            iprstatus=c_iprstatus
                        )
                    )
                # PRODUCTION YEAR
                c_year_from = c_filter.get("yearfrom")
                c_year_to = c_filter.get("yearto")
                if c_year_from is not None or c_year_to is not None:
                    # set defaults if year is missing
                    c_year_from = "1890" if c_year_from is None else str(c_year_from)
                    c_year_to = "1999" if c_year_to is None else str(c_year_to)
                    date_clauses = []
                    if c_type == "video" or c_type == "all":
                        date_clauses.append(
                            "ANY(item IN creation.production_years WHERE item >= '{yfrom}') "
                            "AND ANY(item IN creation.production_years WHERE item <= '{yto}')".format(
                                yfrom=c_year_from, yto=c_year_to
                            )
                        )
                    if c_type == "image" or c_type == "text" or c_type == "all":
                        date_clauses.append(
                            "ANY(item IN creation.date_created WHERE substring(item, 0, 4) >= '{yfrom}') "
                            "AND ANY(item IN creation.date_created WHERE substring(item, 0 , 4) <= '{yto}')".format(
                                yfrom=c_year_from, yto=c_year_to
                            )
                        )
                    filters.append(
                        "MATCH (creation) WHERE {clauses}".format(
                            clauses=" or ".join(date_clauses)
                        )
                    )
                # ANNOTATED TERMS
                terms = c_filter.get("terms")
                if terms:
                    term_clauses = []
                    iris = [term["iri"] for term in terms if "iri" in term]
                    if iris:
                        term_clauses.append(f"term.iri IN {iris}")
                    free_terms = [
                        term["label"]
                        for term in terms
                        if "iri" not in term and "label" in term
                    ]
                    if free_terms:
                        term_clauses.append(f"term.value IN {free_terms}")
                    if term_clauses:
                        filters.append(
                            "MATCH (i)<-[:SOURCE]-(anno2)-[:HAS_BODY]-(term) WHERE {clauses}".format(
                                clauses=" or ".join(term_clauses)
                            )
                        )

        query = (
            "{starters} MATCH (anno:Annotation)"
            " {filters} "
            "WITH body, i, cityPosition, creation, collect(distinct title) AS titles "
            "RETURN DISTINCT body, {projections} {orderBy}".format(
                starters=" ".join(starters),
                filters=" ".join(filters),
                projections=", ".join(projections),
                orderBy=order_by,
            )
        )
        data = []
        result = self.graph.cypher(query)
        for row in result:
            # AD-HOC implementation at the moment
            body = self.graph.ResourceBody.inflate(row[0])
            res = {"iri": body.iri, "name": body.name, "spatial": body.spatial}
            res["sources"] = []
            for source in row[1]:
                creation = {
                    "uuid": source["uuid"],
                    "external_ids": source["external_ids"],
                    "rights_status": source["rights_status"],
                    "type": source["type"],
                }
                # PRODUCTION YEAR: get the first year in the array
                if "production_years" in source:
                    creation["year"] = source["production_years"][0]
                elif "date_created" in source:
                    creation["year"] = source["date_created"][0]
                # TITLE
                if "identifying_title" in source:
                    creation["title"] = source["identifying_title"]
                elif "titles" in source and len(source["titles"]) > 0:
                    # at the moment get the first always!
                    title_node = self.graph.Title.inflate(source["titles"][0])
                    creation["title"] = title_node.text
                res["sources"].append(creation)

            res["distance"] = row[2]
            data.append(res)

        return self.response(data)
