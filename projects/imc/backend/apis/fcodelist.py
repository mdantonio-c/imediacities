# # -*- coding: utf-8 -*-

# """
# Expose the codelists
# """
# import json
# from restapi.utilities.logs import log
# from restapi.rest.definition import EndpointResource
# from restapi.exceptions import RestApiException
# from restapi.protocols.bearer import authentication
# from restapi.utilities.htmlcodes import hcodes
# from restapi import decorators as decorate


# class Fcodelist(EndpointResource):

#     # schema_expose = True
#     labels = ['fcodelist']
#     GET = {'/fcodelist/<codelist>': {'summary': 'GET codelists', 'description': 'Returns a codelist', 'parameters': [{'name': 'lang', 'in': 'query', 'description': 'Language of the codelist', 'type': 'string'}], 'responses': {'200': {'description': 'A codelist.'}, '404': {'description': 'Codelist does not exist.'}}}}

#     @decorate.catch_error()
#     @authentication.required()
#     def get(self, codelist=None):
#         """Get the codelists."""
#         log.debug('load the codelist: ' + codelist)
#         input_parameters = self.get_input()
#         lang = input_parameters['lang']
#         if lang is None:
#             lang = 'en'
#         filename = codelist + '.json'
#         filepath = 'imc/fcodelist/' + lang + '/' + filename
#         log.debug('filepath: ' + filepath)
#         try:
#             data = json.load(open(filepath))
#             return self.force_response(data)
#         except FileNotFoundError as err:
#             log.warning('Codelist file not found: ' + filepath)
#             raise RestApiException(
#                 "Warning: codelist not available", status_code=hcodes.HTTP_BAD_NOTFOUND
#             )
