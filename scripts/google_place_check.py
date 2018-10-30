# -*- coding: utf-8 -*-

import http.client
from urllib.parse import urlencode
import requests
# import json
from utilities.logs import get_logger
from imc.models.neo4j import ResourceBody
from restapi.flask_ext import get_debug_instance
from restapi.flask_ext.flask_neo4j import NeoModel
graph = get_debug_instance(NeoModel)

log = get_logger(__name__)

GOOGLE_API_KEY = 'AIzaSyCkSQ5V_EWELQ6UCvVGBwr3LCriTAfXypI'
GOOGLE_MAPS_API_URL = 'https://maps.googleapis.com/maps/api/place/details/json'

results = graph.cypher("MATCH (n:ResourceBody) WHERE n.spatial IS NOT NULL RETURN n")
invalid = 0
if len(results) > 0:

    for p in [ResourceBody.inflate(row[0]) for row in results]:
        # placeid 'ChIJC8RR6ZjUf0cRQZSkWwF84aI'
        params = urlencode({
            'placeid': p.iri,
            'key': GOOGLE_API_KEY
        })
        resp = requests.get(GOOGLE_MAPS_API_URL, params=params)
        # log.debug('request url %s' % resp.url)
        data = resp.json()
        # log.debug(data)
        if data['status'] == 'INVALID_REQUEST':
            # ignore invalid iri
            continue
        if 'result' not in data:
            continue
        if data['result']['name'] == p.name:
            # ignore valid names
            continue
        invalid += 1
        log.info("Invalid place name ('{}') for IRI: {}. Valid name is '{}'".format(p.name, p.iri, data['result']['name']))

    log.info('Place check completed: total invalid places = %s' % invalid)
