# -*- coding: utf-8 -*-

"""
Search endpoint

@author: Giuseppe Trotta <g.trotta@cineca.it>
"""
from flask import request

from rapydo.utils.logs import get_logger
from rapydo import decorators as decorate
from rapydo.services.neo4j.graph_endpoints import GraphBaseOperations
from rapydo.services.neo4j.graph_endpoints import catch_graph_exceptions

logger = get_logger(__name__)


#####################################
class Search(GraphBaseOperations):

    @decorate.catch_error()
    @catch_graph_exceptions
    def post(self):

        self.initGraph()
        data = []

        # Retrieve the JSON data from the Request and store it in local
        # variable
        jsonData = request.get_json(cache=False)
        attr = {}
        # Iterate over the JSON Data and print the data on console
        for key in jsonData:
            attr[key] = jsonData[key]
            logger.debug("%s = %s" % (key, jsonData[key]))

        if attr['term']:
            videos = self.graph.AVEntity.nodes.filter(
                identifying_title__contains=attr['term'])
        else:
            videos = self.graph.AVEntity.nodes.all()

        for v in videos:
            # FIXME implement a serializer module for all neo models
            res = {}
            item = v.item.single()
            res["uuid"] = item.uuid
            res["thumbnail"] = item.thumbnail
            res["duration"] = item.duration
            res["framerate"] = item.framerate
            if item.digital_format:
                res["digital_format"] = {}
                res["digital_format"]["container"] = item.digital_format[0]
                res["digital_format"]["coding"] = item.digital_format[1]
                res["digital_format"]["format"] = item.digital_format[2]
                res["digital_format"]["resolution"] = item.digital_format[3]
            # res["dimension"] = item.dimension
            # res["dimension_unit"] = item.dimension_unit
            res["uri"] = item.uri
            res["type"] = item.item_type

            # add creation
            video = {}
            video["title"] = v.identifying_title
            descriptions = []
            video["production_years"] = v.production_years
            for d in v.descriptions:
                descriptions.append(d.text)
            video["descriptions"] = descriptions
            keywords = []
            for k in v.keywords:
                term = {}
                term['term'] = k.term
                term['type'] = k.keyword_type
                keywords.append(term)
            video["keywords"] = keywords
            # video = jsonify(v)
            res["creation"] = video

            data.append(res)

        return self.force_response(data)
