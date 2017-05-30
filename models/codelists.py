

TITLE_RELASHIONSHIPS = (
    ('00', 'unspecified'),
    ('01', 'original'),
    ('02', 'working'),
    ('03', 'former'),
    ('04', 'distribution'),
    ('05', 'abbreviated'),
    ('06', 'translated'),
    ('07', 'alternative'),
    ('08', 'explanatory'),
    ('09', 'uniform'),
    ('10', 'other'))

KEYWORD_TYPES = (
    ('00', 'Building'),
    ('01', 'Person'),
    ('02', 'Subject'),
    ('03', 'Genre'),
    ('04', 'Place'),
    ('05', 'Form'),
    ('06', 'Georeference')
    # FIXME just an example here
)

DESCRIPTION_TYPES = (
    ('01', 'synopsis'),
    ('02', 'short list'),
    ('03', 'review')
    # FIXME just an example here
)

LANGUAGE_USAGES = (
    ('01', 'original spoken dialogue'),
    ('02', 'dubbing'),
    ('03', 'subtitles'),
    ('04', 'voice over commentary'),
    # FIXME just an example here
)

AGENT_TYPES = (
    ('P', 'person'),
    ('C', 'corporate')
)

SEXES = (
    ('M', 'Male'),
    ('F', 'Female')
)

PROVIDER_SCHEMES = (
    ('ISIL', 'ISIL code'),
    ('ACRO', 'Institution acronym')
)

VIDEO_SOUND = (
    ('NO_SOUND', 'without sound'),
    ('WITH_SOUND', 'with sound')
)

NON_AV_ENTITY_TYPES = (
    ('01', 'image'),
    ('02', 'text')
)

NON_AV_ENTITY_SPECIFIC_TYPES = (
    ('01', 'photograph'),
    ('02', 'poster'),
    ('03', 'letter')
)  # FIXME just an ex. here: Based on the values of IMC content providers

ORPHAN_STATUS = (
    ('UNK', 'Unknown, orphan status not determined'),
    ('ORP', 'Orphan'),
    ('POR', 'Partial orphan (at least one assumed rightholder unknown)'),
    ('NOR', 'Not orphan'),
    ('NAP', 'Not applicable (use with unknown rights status, \
        or determined to be public')
)

# Preso dal Deliverable D4.2 Innovative e-environments for Research on Cities
# and the Media – n°693559

# Rights Status
# In copyright
# EU Orphan Work
# In copyright - Educational use permitted
# In copyright - Non-commercial use permitted
# Public Domain

# from FORWARD codelist
# IPR_STATUS = (
#     ('UNK', 'Unknown, IPR status not determined'),
#     ('ACP', 'Assumed to be in copyroght'),
#     ('ICP', 'Determined to be in copyright'),
#     ('PDO', 'Public domain, all rights expired')
# )

IPR_STATUS = (
    'Copyright protected',
    'Not copyright protected'
)
