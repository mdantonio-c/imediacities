"""
Manage the lists of the researcher
"""
import re

from imc.endpoints import IMCEndpoint
from imc.models import Target
from restapi import decorators
from restapi.config import get_backend_url
from restapi.connectors import neo4j
from restapi.exceptions import BadRequest, Conflict, Forbidden, NotFound, ServerError
from restapi.models import fields
from restapi.utilities.logs import log

TARGET_PATTERN = re.compile("(item|shot):([a-z0-9-])+")

__author__ = "Giuseppe Trotta(g.trotta@cineca.it)"


class Lists(IMCEndpoint):

    labels = ["list"]

    @decorators.auth.require_all("Researcher")
    @decorators.use_kwargs(
        {
            "r_uuid": fields.Str(
                required=False,
                data_key="researcher",
                description="Researcher uuid",
            ),
            "belong_item": fields.Str(
                required=False,
                data_key="item",
                description="Item uuid (used to check whether the item belongs to the list or not)",
            ),
            "nb_items": fields.Bool(
                required=False,
                missing=False,
                data_key="includeNumberOfItems",
            ),
        },
        location="query",
    )
    @decorators.endpoint(
        path="/lists",
        summary="Get a list of the researcher",
        description="Returns all the list of a researcher.",
        responses={
            200: "The list of the researcher.",
            403: "The user is not authorized to perform this operation.",
            404: "The requested list does not exist.",
        },
    )
    @decorators.endpoint(
        path="/lists/<list_id>",
        summary="Get a list of the researcher",
        description="Returns all the list of a researcher.",
        responses={
            200: "The list of the researcher.",
            403: "The user is not authorized to perform this operation.",
            404: "The requested list does not exist.",
        },
    )
    def get(self, list_id=None, r_uuid=None, belong_item=None, nb_items=False):
        """ Get all the list of a user or a certain list if an id is provided."""
        self.graph = neo4j.get_instance()

        iamadmin = self.verify_admin()
        researcher = self.get_user() if not iamadmin else None
        if iamadmin and list_id is None and r_uuid is not None:
            researcher = self.graph.User.nodes.get_or_none(uuid=r_uuid)
            if not researcher:
                log.debug("Researcher with uuid {} does not exist", r_uuid)
                raise NotFound("Please specify a valid researcher id")

        user_match = ""
        optional_match = ""
        if researcher:
            user_match = (
                "MATCH (n)-[:LST_BELONGS_TO]->(:User {{uuid:'{user}'}})".format(
                    user=researcher.uuid
                )
            )
            log.debug("researcher: {} {}", researcher.name, researcher.surname)

        if nb_items:
            optional_match = "OPTIONAL MATCH (n)-[r:LST_ITEM]->(:ListItem)"

        if list_id:
            res = self.graph.List.nodes.get_or_none(uuid=list_id)
            if not res:
                log.debug("List with uuid {} does not exist", list_id)
                raise NotFound("Please specify a valid list id")

            creator = res.creator.single()
            if not iamadmin and researcher.uuid != creator.uuid:
                raise Forbidden(
                    "You are not allowed to get a list that does not belong to you",
                )
            user_list = self.getJsonResponse(res)
            if iamadmin and researcher is None:
                user_list["creator"] = {
                    "uuid": creator.uuid,
                    "name": creator.name,
                    "surname": creator.surname,
                }

            if belong_item is not None:
                found = False
                for i in res.items.all():
                    if i.downcast().uuid == belong_item:
                        found = True
                        break
                user_list["belong"] = found

            if nb_items:
                user_list["nb_frames"] = len(res.items)

            return self.response(user_list)

        count_items = ", count(r)" if nb_items else ""
        query = (
            "MATCH (n:List) "
            "{match} "
            "{optional} "
            "RETURN DISTINCT(n){counter}".format(
                match=user_match, optional=optional_match, counter=count_items
            )
        )
        log.debug("query: {}", query)

        # get total number of lists
        # numels = [row[0] for row in self.graph.cypher(count)][0]
        # log.debug("Total number of lists: {0}", numels)

        data = []
        # meta_response = {"totalItems": numels}
        results = self.graph.cypher(query)
        # for res in [self.graph.List.inflate(row[0]) for row in results]:
        for row in results:
            res = self.graph.List.inflate(row[0])
            user_list = self.getJsonResponse(res)
            if iamadmin and researcher is None:
                creator = res.creator.single()
                user_list["creator"] = {
                    "uuid": creator.uuid,
                    "name": creator.name,
                    "surname": creator.surname,
                }
            if belong_item is not None:
                for i in res.items.all():
                    if i.downcast().uuid == belong_item:
                        user_list["belong"] = True
                        break
            if nb_items:
                user_list["nb_items"] = row[1]
            data.append(user_list)

        # return self.response(data, meta=meta_response)
        return self.response(data)

    @decorators.auth.require_all("Researcher")
    @decorators.database_transaction
    @decorators.use_kwargs(
        {"name": fields.Str(required=True), "description": fields.Str(required=True)}
    )
    @decorators.endpoint(
        path="/lists",
        summary="Create a new list",
        responses={
            201: "List created successfully.",
            400: "There is no content present in the request body or the content is not valid for list.",
            403: "The user is not authorized to perform this operation.",
            409: "There is already a list with that name.",
        },
    )
    def post(self, name, description):
        """
        Create a new list.

        Only a researcher can create a list. Both name and description are
        mandatory. There can not be lists with the same name.
        """
        log.debug("create a new list")

        self.graph = neo4j.get_instance()
        user = self.get_user()
        # Can't happen since auth is required
        if not user:  # pragma: no cover
            raise ServerError("User misconfiguration")

        # check if there is already a list with the same name belonging to the user.
        results = self.graph.cypher(
            "MATCH (l:List)-[:LST_BELONGS_TO]-(:User {{uuid:'{user}'}})"
            " WHERE l.name =~ '(?i){name}' return l".format(
                user=user.uuid, name=self.graph.sanitize_input(name)
            )
        )
        duplicate = [self.graph.List.inflate(row[0]) for row in results]
        if duplicate:
            raise Conflict(
                "There is already a list with the same name belonging to you"
            )

        created_list = self.graph.List(name=name, description=description).save()
        # connect the creator
        created_list.creator.connect(user)
        log.debug("List created successfully. UUID {}", created_list.uuid)
        return self.response(self.getJsonResponse(created_list), code=201)

    @decorators.auth.require_all("Researcher")
    @decorators.database_transaction
    @decorators.use_kwargs(
        {"name": fields.Str(required=True), "description": fields.Str(required=True)}
    )
    @decorators.endpoint(
        path="/lists/<list_id>",
        summary="Update a list",
        description="Update a list of the researcher",
        responses={
            200: "List updated successfully.",
            400: "There is no content in the request body or the content is not valid",
            403: "The user is not authorized to perform this operation.",
            404: "List does not exist.",
            409: "There is already another list with the same name among your lists.",
        },
    )
    def put(self, list_id, name, description):
        """ Update a list. """
        log.debug("Update list with uuid: {}", list_id)
        self.graph = neo4j.get_instance()
        user_list = self.graph.List.nodes.get_or_none(uuid=list_id)
        if not user_list:
            log.debug("List with uuid {} does not exist", list_id)
            raise NotFound("Please specify a valid list id")

        user = self.get_user()
        # Can't happen since auth is required
        if not user:  # pragma: no cover
            raise ServerError("User misconfiguration")

        creator = user_list.creator.single()
        if not user or user.uuid != creator.uuid:
            raise Forbidden(
                "You cannot update an user list that does not belong to you"
            )

        # cannot update a list name if that name is already used for another list
        results = self.graph.cypher(
            "MATCH (l:List) WHERE l.uuid <> '{uuid}'"
            " MATCH (l)-[:LST_BELONGS_TO]-(:User {{uuid:'{user}'}})"
            " WHERE l.name =~ '(?i){name}' return l".format(
                uuid=list_id,
                user=user.uuid,
                name=self.graph.sanitize_input(name),
            )
        )
        duplicate = [self.graph.List.inflate(row[0]) for row in results]
        if duplicate:
            raise Conflict(f"You already have a list with this name: {name}")
        # update the list
        user_list.name = name.strip()
        user_list.description = description.strip()
        updated_list = user_list.save()
        log.debug("List successfully updated. UUID {}", updated_list.uuid)
        return self.response(self.getJsonResponse(updated_list))

    @decorators.auth.require_all("Researcher")
    @decorators.database_transaction
    @decorators.endpoint(
        path="/lists/<list_id>",
        summary="Delete a list",
        description="Delete a list of the researcher.",
        responses={
            204: "List deleted successfully.",
            403: "The user is not authorized to perform this operation.",
            404: "List does not exist.",
        },
    )
    def delete(self, list_id):
        """ Delete a list. """
        log.debug("delete list {}", list_id)

        self.graph = neo4j.get_instance()
        user_list = self.graph.List.nodes.get_or_none(uuid=list_id)
        if not user_list:
            log.debug("List with uuid {} does not exist", list_id)
            raise NotFound("Please specify a valid list id")

        user = self.get_user()

        # Can't happen since auth is required
        if not user:  # pragma: no cover
            raise ServerError("User misconfiguration")

        log.debug("current user: {} - {}", user.email, user.uuid)
        iamadmin = self.verify_admin()
        log.debug("current user is admin? {0}", iamadmin)

        creator = user_list.creator.single()
        if user.uuid != creator.uuid and not iamadmin:
            raise Forbidden(
                "You cannot delete an user list that does not belong to you"
            )

        # delete the list
        user_list.delete()
        log.debug("List delete successfully. UUID {}", list_id)
        return self.empty_response()


class ListItems(IMCEndpoint):
    """ List of items in a list. """

    labels = ["list_items"]

    @decorators.auth.require_all("Researcher")
    @decorators.endpoint(
        path="/lists/<list_id>/items/<item_id>",
        summary="List of items in a list.",
        description="Get all the items of a list. the result supports paging.",
        responses={
            200: "An list of items.",
            403: "The user is not authorized to perform this operation.",
            404: "List does not exist.",
        },
    )
    @decorators.endpoint(
        path="/lists/<list_id>/items",
        summary="List of items in a list.",
        description="Get all the items of a list. the result supports paging.",
        responses={
            200: "An list of items.",
            403: "The user is not authorized to perform this operation.",
            404: "List does not exist.",
        },
    )
    def get(self, list_id, item_id=None):
        """Get all the items of a list or a certain item of that list if an
        item id is provided."""
        self.graph = neo4j.get_instance()
        try:
            user_list = self.graph.List.nodes.get(uuid=list_id)
        except self.graph.List.DoesNotExist:
            log.debug("List with uuid {} does not exist", list_id)
            raise NotFound("Please specify a valid list id")
        # am I the owner of the list? (allowed also to admin)
        user = self.get_user()
        # Can't happen since auth is required
        if not user:  # pragma: no cover
            raise ServerError("User misconfiguration")

        iamadmin = self.auth.is_admin(user)
        creator = user_list.creator.single()
        if user.uuid != creator.uuid and not iamadmin:
            raise Forbidden(
                "You are not allowed to get a list that does not belong to you",
            )
        if item_id is not None:
            log.debug(
                "Get item <{}> of the list <{}, {}>".format(
                    item_id, user_list.uuid, user_list.name
                )
            )
            # Find item with uuid <item_id> in the user_list
            # res = user_list.items.search(uuid=item_id)
            results = self.graph.cypher(
                "MATCH (l:List {{uuid:'{uuid}'}})"
                " MATCH (l)-[:LST_ITEM]->(i:ListItem {{uuid:'{item}'}})"
                " RETURN i"
                "".format(uuid=list_id, item=item_id)
            )
            res = [self.graph.ListItem.inflate(row[0]) for row in results]
            if not res:
                raise NotFound(
                    "Item <{}> is not connected to the list <{}, {}>".format(
                        item_id, user_list.uuid, user_list.name
                    )
                )
            return self.response(self.get_list_item_response(res[0]))

        log.debug(
            "Get all the items of the list <{}, {}>", user_list.uuid, user_list.name
        )

        data = []
        for list_item in user_list.items.all():
            data.append(self.get_list_item_response(list_item))
        return self.response(data)

    @decorators.auth.require_all("Researcher")
    @decorators.database_transaction
    @decorators.use_kwargs(Target)
    @decorators.endpoint(
        path="/lists/<list_id>/items",
        summary="Add an item to a list.",
        responses={
            204: "Item added successfully.",
            400: "Bad request body or target node does not exist.",
            403: "The user is not authorized to perform this operation.",
            404: "List does not exist.",
            409: "The item is already connected to that list.",
        },
    )
    def post(self, list_id, target):
        """ Add an item to a list. """
        log.debug("Add an item to list {} with target {}", list_id, target)

        self.graph = neo4j.get_instance()
        user_list = self.graph.List.nodes.get_or_none(uuid=list_id)
        if not user_list:
            log.debug("List with uuid {} does not exist", list_id)
            raise NotFound("Please specify a valid list id")

        # am I the creator of the list?
        user = self.get_user()
        # Can't happen since auth is required
        if not user:  # pragma: no cover
            raise ServerError("User misconfiguration")

        creator = user_list.creator.single()
        if user.uuid != creator.uuid:
            raise Forbidden(
                "You cannot add an item to a list that does not belong to you"
            )

        target_type = target.get("type")
        target_id = target.get("id")

        log.debug("target type: {}, target id: {}", target_type, target_id)
        targetNode = None
        if target_type == "item":
            targetNode = self.graph.Item.nodes.get_or_none(uuid=target_id)
        elif target_type == "shot":
            targetNode = self.graph.Shot.nodes.get_or_none(uuid=target_id)

        if targetNode is None:
            raise BadRequest(f"Target [{target_type}:{target_id}] does not exist")
        # check if the incoming target is already connected to the list
        if targetNode.lists.is_connected(user_list):
            raise Conflict(
                f"The item is already connected to the list {list_id}, {user_list.name}"
            )
        # connect the target to the list
        user_list.items.connect(targetNode)
        log.debug(
            "Item {} added successfully to list <{}, {}>",
            target,
            list_id,
            user_list.name,
        )
        # 204: return empty response (?)
        self.empty_response()

    @decorators.auth.require_all("Researcher")
    @decorators.database_transaction
    @decorators.endpoint(
        path="/lists/<list_id>/items/<item_id>",
        summary="Delete an item from a list.",
        responses={
            204: "Item deleted successfully.",
            403: "The user is not authorized to perform this operation.",
            404: "List or item does not exist.",
        },
    )
    def delete(self, list_id, item_id):
        """ Delete an item from a list. """
        self.graph = neo4j.get_instance()

        user_list = self.graph.List.nodes.get_or_none(uuid=list_id)
        if not user_list:
            log.debug("List with uuid {} does not exist", list_id)
            raise NotFound("Please specify a valid list id")

        log.debug(
            "delete item <{}> from the list <{}, {}>",
            item_id,
            user_list.uuid,
            user_list.name,
        )
        # am I the creator of the list? (always allowed to admin)
        user = self.get_user()
        # Can't happen since auth is required
        if not user:  # pragma: no cover
            raise ServerError("User misconfiguration")

        iamadmin = self.verify_admin()
        creator = user_list.creator.single()
        if user.uuid != creator.uuid and not iamadmin:
            raise Forbidden(
                "You are not allowed to delete from a list that does not belong to you",
            )

        matched_item = None
        for list_item in user_list.items.all():
            item = list_item.downcast()
            if item.uuid == item_id:
                matched_item = item
                break

        if matched_item is None:
            list_info = f"{user_list.uuid}, {user_list.name}"
            raise NotFound(f"Item <{item_id}> does not belong the list {list_info}")

        # disconnect the item
        user_list.items.disconnect(matched_item)
        log.debug(
            "Item <{}> remeved from the list <{}, {}>successfully.",
            item_id,
            user_list.uuid,
            user_list.name,
        )
        return self.empty_response()

    def get_list_item_response(self, list_item):
        # look at the most derivative class
        # expected list_item of type :Item or :Shot
        mdo = list_item.downcast()
        item = None
        if isinstance(mdo, self.graph.Item):
            item = mdo
        elif isinstance(mdo, self.graph.Shot):
            item = mdo.item.single()
        else:
            raise ValueError("Invalid ListItem instance.")
        creation = item.creation.single()
        if creation is None:
            raise ValueError(f"Very strange. Item <{item.uuid}> with no metadata")
        creation = creation.downcast()

        res = self.getJsonResponse(mdo, max_relationship_depth=0)
        api_url = get_backend_url()
        res["links"] = {}
        if isinstance(mdo, self.graph.Item):
            # always consider v2 properties if exists
            v2 = item.other_version.single()
            content_type = "videos" if item.item_type == "Video" else "images"
            res["links"][
                "content"
            ] = f"{api_url}/api/{content_type}/{creation.uuid}/content?type={content_type[:-1]}"
            res["links"]["thumbnail"] = (
                f"{api_url}/api/{content_type}/{creation.uuid}/content?type=thumbnail&size=large"
                if item.item_type == "Video" or v2 is None
                else f"{api_url}/api/{content_type}/{creation.uuid}/content?type={content_type[:-1]}"
            )
        else:
            # SHOT
            res["links"][
                "content"
            ] = f"{api_url}/api/videos/{creation.uuid}/content?type=video"
            # THIS IS WRONG. SHOULD BE get_frontend_url
            res["links"]["webpage"] = f"{api_url}/app/catalog/videos/{creation.uuid}"
            res["links"][
                "thumbnail"
            ] = f"{api_url}/api/shots/{mdo.uuid}?content=thumbnail"
            # add some video item attributes
            res["item"] = {
                "digital_format": item.digital_format,
                "dimension": item.dimension,
                "duration": item.duration,
                "framerate": item.framerate,
            }

        res["creation_id"] = creation.uuid
        res["rights_status"] = creation.get_rights_status_display()
        for record_source in creation.record_sources.all():
            provider = record_source.provider.single()
            res["city"] = provider.city
            break
        # add title
        for idx, t in enumerate(creation.titles.all()):
            # get default
            if not idx:
                res["title"] = t.text
            # override with english text
            if t.language and t.language == "en":
                res["title"] = t.text
        # add description
        for idx, desc in enumerate(creation.descriptions.all()):
            # get default
            if not idx:
                res["description"] = desc.text
            # override with english text
            if desc.language and desc.language == "en":
                res["description"] = desc.text
        # add contributor
        for agent in creation.contributors.all():
            rel = creation.contributors.relationship(agent)
            if (
                item.item_type == "Video"
                and agent.names
                and "Director" in rel.activities
            ):
                # expected one in the list
                res["director"] = agent.names[0]
                break
            if (
                item.item_type == "Image"
                and agent.names
                and "Creator" in rel.activities
            ):
                # expected one in the list
                res["creator"] = agent.names[0]
                break
        # add production year
        if item.item_type == "Image" and creation.date_created:
            res["production_year"] = creation.date_created[0]
        if item.item_type == "Video" and creation.production_years:
            res["production_year"] = creation.production_years[0]
        # add video format
        if item.item_type == "Video":
            video_format = creation.video_format.single()
            if video_format is not None:
                res["video_format"] = self.getJsonResponse(
                    video_format, max_relationship_depth=0
                )
        # add notes and links
        res["annotations"] = {}
        notes = mdo.annotation.search(annotation_type="DSC", private=False)
        if notes:
            res["annotations"]["notes"] = []
            for n in notes:
                # expected single body here
                note_text = n.bodies.single().downcast()
                res["annotations"]["notes"].append(
                    {"text": note_text.value, "language": note_text.language}
                )
        links = mdo.annotation.search(annotation_type="LNK", private=False)
        if links:
            res["annotations"]["links"] = []
            for link in links:
                link_text = link.bodies.single().downcast()
                # a link can have a ReferenceBody
                if not isinstance(link_text, self.graph.TextualBody):
                    continue
                res["annotations"]["links"].append(link_text.value)
            if not res["annotations"]["links"]:
                del res["annotations"]["links"]
        if not res["annotations"]:
            del res["annotations"]
        return res
