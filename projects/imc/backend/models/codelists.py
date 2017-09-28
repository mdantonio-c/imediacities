# -*- coding: utf-8 -*-


def fromDescription(descr, codelist):
    """
    Returns the matched element by description in the give codelist. None
    otherwise.
    """
    res = [item for item in codelist if item[1].lower() == descr.lower()]
    return res[0] if res else None


def fromCode(descr, codelist):
    """
    Returns the matched element by code in the give codelist. None otherwise.
    """
    res = [item for item in codelist if item[0].lower() == descr.lower()]
    return res[0] if res else None


CONTENT_TYPES = (
    ('Video', 'Video'),
    ('Image', 'Image'),
    ('Text',  'Text')
)

SOURCE_TYPES = (
    ('Metadata', 'Metadata'),
    ('Content', 'Content')
)

AV_TITLE_TYPES = (
    ('Original title',     'Original release title'),
    ('Other title',        'Alternative title, Variant title'),
    ('Series title',       'Title of series'),
    ('Serial title',       'Title of serial'),
    ('Episode title',      'Chapter title, Title of episode, Title of chapter'),
    ('TV title',           'Television title'),
    ('Version title',      'Version title'),
    ('Translated title',   'Literal translation title'),
    ('Working title',      'Working title'),
    ('Segment title',      'Story title'),
    ('Spelling variation', 'Spelling variation'),
    ('Archive title',      'Archive title'),
    ('Subtitle',           'Additional title'),
    ('Distribution title', 'Release title'),
    ('Tagline',            'Tagline'),
    ('Compilation title',  'Compilation title')
)

NON_AV_TITLE_TYPE = (
    ('01', 'Main title'),
    ('02', 'Alternative title')
)

AV_TITLE_UNIT = (
    ('Part',    'Part'),
    ('Episode', 'Episode'),
    ('Season',  'Season'),
    ('Volume',  'Volume'),
    ('Issue',   'Issue')
)

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
)

DESCRIPTION_TYPES = (
    ('01', 'Synopsis'),
    ('02', 'Content description'),
    ('03', 'Shotlist'),
    ('04', 'Dialogue'),
    ('05', 'Review snippet'),
    ('06', 'Intertitles'),
    ('07', 'Broadcast commentary')
)

LANGUAGE_USAGES = (
    ('01', 'Additional dubbed language'),
    ('02', 'Additional original language'),
    ('03', 'Audio'),
    ('04', 'Audio description'),
    ('05', 'Caption'),
    ('06', 'Closed caption'),
    ('07', 'Descriptive video information'),
    ('08', 'Director\'s commentary'),
    ('09', 'Dubbed commentary'),
    ('10', 'Dubbed dialogue'),
    ('11', 'Dubbed narration'),
    ('12', 'Educational notes'),
    ('13', 'Interviewee language'),
    ('14', 'Interviewer language'),
    ('15', 'Main dubbed language'),
    ('16', 'Main original language'),
    ('17', 'Open caption'),
    ('18', 'Original commentary'),
    ('19', 'Original narration'),
    ('20', 'Song lyrics'),
    ('21', 'Subtitle'),
    ('22', 'Supplemental'),
    ('23', 'Supplemental commentary'),
    ('24', 'Supplementary audio programme'),
    ('25', 'Text'),
    ('26', 'Text description for the hard-of-hearing'),
    ('27', 'Transcript'),
    ('28', 'Voice over')
)

AGENT_TYPES = (
    ('P', 'person'),
    ('C', 'corporate')
)

SEXES = (
    ('M', 'Male'),
    ('F', 'Female')
)

TYPE_OF_ACTIVITY = (
    ('001', 'Actor'),
    ('002', 'Actress'),
    ('003', 'Adapted by'),
    ('004', 'Aerial photographer'),
    ('005', 'Animal trainer'),
    ('006', 'Animation camera'),
    ('007', 'Animation director'),
    ('008', 'Animator'),
    ('009', 'Annotator'),
    ('010', 'Applicant'),
    ('011', 'Architect'),
    ('012', 'Armorer'),
    ('013', 'Art director'),
    ('014', 'Artist'),
    ('015', 'Assistant art director'),
    ('016', 'Assistant camera operator'),
    ('017', 'Assistant chief lighting technician'),
    ('018', 'Assistant director'),
    ('019', 'Assistant editor'),
    ('020', 'Assistant location manager'),
    ('021', 'Assistant make-up artist'),
    ('022', 'Assistant producer'),
    ('023', 'Associate producer'),
    ('024', 'Athlete'),
    ('025', 'Author(s)'),
    ('026', 'Book designer'),
    ('027', 'Boom operator'),
    ('028', 'Camera operator'),
    ('029', 'Casting'),
    ('030', 'Caterer'),
    ('031', 'Character designer'),
    ('032', 'Choreographer'),
    ('033', 'Clapper loader'),
    ('034', 'Cleanup'),
    ('035', 'Cleric'),
    ('036', 'Collector'),
    ('037', 'Colour consultant'),
    ('038', 'Colour timer'),
    ('039', 'Commentator'),
    ('040', 'Commissioner'),
    ('041', 'Composer'),
    ('042', 'Conception'),
    ('043', 'Conductor'),
    ('044', 'Construction manager'),
    ('045', 'Consultant'),
    ('046', 'Cooperation'),
    ('047', 'Co-producer'),
    ('048', 'Co-production'),
    ('049', 'Costume designer'),
    ('050', 'Costume maker'),
    ('051', 'Costume supervisor'),
    ('052', 'Costume supplier'),
    ('053', 'Costumer'),
    ('054', 'Costumer assistant'),
    ('055', 'Costumes'),
    ('056', 'Crane operator'),
    ('057', 'Creator'),
    ('058', 'Dancer'),
    ('059', 'Designer'),
    ('060', 'Dialogue'),
    ('061', 'Dialogue coach'),
    ('062', 'Dialogue editor'),
    ('063', 'Director'),
    ('064', 'Director of photography'),
    ('065', 'Director of publicity'),
    ('066', 'Director theatre/opera/musical'),
    ('067', 'Distributor'),
    ('068', 'Dolly grip'),
    ('069', 'Double'),
    ('070', 'Dramaturgy'),
    ('071', 'Dubbing'),
    ('072', 'Dubbing director'),
    ('073', 'Dubbing editor'),
    ('074', 'Dubbing speaker'),
    ('075', 'Editor'),
    ('076', 'Editorial staff'),
    ('077', 'Electrician'),
    ('078', 'Engineer'),
    ('079', 'Entrepreneur'),
    ('080', 'Executive producer'),
    ('081', 'Exhibitor'),
    ('082', 'Fight arranger'),
    ('083', 'Film historian'),
    ('084', 'Film reviewer'),
    ('085', 'Filmmaker'),
    ('086', 'Film-related activity'),
    ('087', 'Focus puller'),
    ('088', 'Foley artist'),
    ('089', 'Funding'),
    ('090', 'Gaffer'),
    ('091', 'Generator operator'),
    ('092', 'Gowns'),
    ('093', 'Greensman'),
    ('094', 'Grip'),
    ('095', 'Hairdresser'),
    ('096', 'Honoured to'),
    ('097', 'Illustrator'),
    ('098', 'Interviewer'),
    ('099', 'Journalist'),
    ('100', 'Jurisprudent'),
    ('101', 'Key grip'),
    ('102', 'Laboratory technician'),
    ('103', 'Layout'),
    ('104', 'Lead man'),
    ('105', 'Lenses manufacturer'),
    ('106', 'Light'),
    ('107', 'Lighter'),
    ('108', 'Line producer'),
    ('109', 'Lithographer'),
    ('110', 'Location manager'),
    ('111', 'Make-up artist'),
    ('112', 'Manufacturer'),
    ('113', 'Medic'),
    ('114', 'Military'),
    ('115', 'Mixer'),
    ('116', 'Model maker'),
    ('117', 'Monarchy'),
    ('118', 'Music'),
    ('119', 'Music arranger'),
    ('120', 'Music composer'),
    ('121', 'Music contractor'),
    ('122', 'Music editor'),
    ('123', 'Music performer'),
    ('124', 'Music supervisor'),
    ('125', 'Narrator'),
    ('126', 'Negative cutter'),
    ('127', 'Non-film activity'),
    ('128', 'Participant'),
    ('129', 'Performer'),
    ('130', 'Photographer'),
    ('131', 'Politician'),
    ('132', 'Poster designer'),
    ('133', 'Post-production assistant'),
    ('134', 'Post-production supervisor'),
    ('135', 'Pre-production'),
    ('136', 'Presenter'),
    ('137', 'Producer'),
    ('138', 'Production accountant'),
    ('139', 'Production assistant'),
    ('140', 'Production company'),
    ('141', 'Production coordinator'),
    ('142', 'Production designer'),
    ('143', 'Production manager'),
    ('144', 'Property man'),
    ('145', 'Property master'),
    ('146', 'Publisher'),
    ('147', 'Publisher'),
    ('148', 'Publishing editor'),
    ('149', 'Puppet designer'),
    ('150', 'Puppeteer'),
    ('151', 'Puppets manufacturer'),
    ('152', 'Researcher'),
    ('153', 'Scenic artist'),
    ('154', 'Scientist'),
    ('155', 'Screen story'),
    ('156', 'Screenplay'),
    ('157', 'Screenplay translation'),
    ('158', 'Script / Continuity'),
    ('159', 'Script supervisor'),
    ('160', 'Series producer'),
    ('161', 'Set decorator'),
    ('162', 'Set decorator assistant'),
    ('163', 'Set designer'),
    ('164', 'Set designer assistant'),
    ('165', 'Singer'),
    ('166', 'Soloist'),
    ('167', 'Song composer'),
    ('168', 'Sound'),
    ('169', 'Sound assistant'),
    ('170', 'Sound designer'),
    ('171', 'Sound editor'),
    ('172', 'Sound engineer'),
    ('173', 'Sound recorder'),
    ('174', 'Sound supervisor'),
    ('175', 'Special effects'),
    ('176', 'Special make-up effects'),
    ('177', 'Sponsor'),
    ('178', 'Stand-in'),
    ('179', 'Steadycam operator'),
    ('180', 'Still photography'),
    ('181', 'Story editor'),
    ('182', 'Storyboard artist'),
    ('183', 'Stunt coordinator'),
    ('184', 'Stunt performer'),
    ('185', 'Supervising animator'),
    ('186', 'Supervising sound editor'),
    ('187', 'Technician'),
    ('188', 'Title designer'),
    ('189', 'Transportation manager'),
    ('190', 'Underwater cameraman'),
    ('191', 'Visual effects'),
    ('192', 'Wardrobe supervisor'),
    ('193', 'Wrangler')
)

PROVIDER_SCHEMES = (
    ('ISIL', 'ISIL code'),
    ('ACRO', 'Institution acronym')
)

IDENTIFIER_SCHEMES = (
    ('ISIL', 'International Standard for Library Institutions and Related Organisations'),
    ('UUID', 'Universally Unique Identifier'),
    ('GUID', 'Globally Unique Identifier'),
    ('URI',  'Uniform Resource Identifier'),
    ('URL',  'Uniform Resource Locator'),
    ('URN',  'Uniform Resource Name'),
    ('ISAN', 'International Standard Audiovisual Number'),
    ('ISBN', 'International Standard Book Number'),
    ('ISSN', 'International Standard Serial Number'),
    ('ISMN', 'International Standard Music Number'),
    ('DOI',  'Digital Object Identifier')
)

VIDEO_SOUND = (
    ('NO_SOUND', 'Without sound'),
    ('WITH_SOUND', 'With sound')
)

NON_AV_TYPES = (
    ('image', 'image'),
    ('text', 'text')
)

ORPHAN_STATUS = (
    ('UNK', 'Unknown, orphan status not determined'),
    ('ORP', 'Orphan'),
    ('POR', 'Partial orphan (at least one assumed rightholder unknown)'),
    ('NOR', 'Not orphan'),
    ('NAP', 'Not applicable (use with unknown rights status, \
        or determined to be public')
)  # REMOVE never used?

RIGHTS_STATUS = (
    ('01', 'In copyright'),
    ('02', 'EU Orphan Work'),
    ('03', 'In copyright - Educational use permitted'),
    ('04', 'In copyright - Non-commercial use permitted'),
    ('05', 'Public Domain')
)

IPR_STATUS = (
    'Copyright protected',
    'Not copyright protected'
)

ASPECT_RATIO = (
    ('01', '1:1,15'),
    ('02', '1:1,19-1:1,21'),
    ('03', '1:1,33-1:1,34'),
    ('04', '1:1,37'),
    ('05', '1:1,66'),
    ('06', '1:1,78'),
    ('07', '1:1,85'),
    ('08', '1:2,21 - 1:2,25'),
    ('09', '1:2,35  Superscope'),
    ('10', '1:2,55'),
    ('11', '1:1,96'),
    ('12', '16:9'),
    ('13', '4:3'),
    ('14', '5:3'),
    ('15', '1:1.75  Widescreen'),
    ('16', 'IMAX 15 perf'),
    ('17', '1:2 Superscope (normal)'),
    ('18', 'Special format'),
)

CARRIER_TYPE = (
    ('01', 'Original negative'),
    ('02', 'Original positive'),
    ('03', 'Duplicate negative'),
    ('04', 'Duplicate positive'),
    ('05', 'Image negative'),
    ('06', 'Image positive'),
    ('07', 'Sound negative'),
    ('08', 'Sound positive'),
    ('09', 'Reversal negative'),
    ('10', 'Reversal positive'),
    ('11', 'Non-film analogue carrier'),
    ('12', 'Video tape'),
    ('13', 'Digital video tape'),
    ('14', 'DVD'),
    ('15', 'Non-film digital carrier'),
    ('16', 'BD')
)

COLOUR = (
    ('01', 'Black & White'),
    ('02', 'Colour'),
    ('03', 'B/W & Colour'),
    ('04', 'Tinted / Toned / Hand coloured'),
    ('05', 'Colour & B/W')
)

# DURATIONFORMAT  Duration of each video in this format HH:MM:SS
GAUGE = (
    ('01',     '8mm film type R'),
    ('02',     '8mm film type S'),
    ('03',              '9,5 mm'),
    ('04',               '16 mm'),
    ('05',              '35 mm'),
    ('06',              '55 mm'),
    ('07',               '65 mm'),
    ('08',              '70 mm'),
    ('09',             '17,5 mm'),
    ('10',               '22 mm'),
    ('11',               '28 mm'),
    ('12',               '30 mm'),
    ('13',             '44,5 mm'),
    ('14',              '68 mm'),
    ('15',      'Special format')
)

NON_AV_SPECIFIC_TYPES = (
    ('01', 'Advertising material'),
    ('02', 'Article'),
    ('03', 'Book'),
    ('04', 'Censorship card'),
    ('05', 'Censorship certificate'),
    ('06', 'Censorship document'),
    ('07', 'Censorship report'),
    ('08', 'Correspondence'),
    ('09', 'Dialogue list'),
    ('10', 'Distribution poster'),
    ('11', 'Drawing'),
    ('12', 'Festival poster'),
    ('13', 'Film still'),
    ('14', 'First release poster'),
    ('15', 'Interview'),
    ('16', 'Manuscript'),
    ('17', 'Monograph'),
    ('18', 'Music'),
    ('19', 'Music sheet'),
    ('20', 'News report'),
    ('21', 'Periodical'),
    ('22', 'Photo'),
    ('23', 'Portrait'),
    ('24', 'Poster'),
    ('25', 'Production design'),
    ('26', 'Production material'),
    ('27', 'Programme'),
    ('28', 'Promotional photo'),
    ('29', 'Rating certificate'),
    ('30', 'Rating report'),
    ('31', 'Registration card'),
    ('32', 'Autograph'),
    ('33', 'Booklet'),
    ('34', 'Cover'),
    ('35', 'Folder'),
    ('36', 'Postcard'),
    ('37', 'Reproduction poster'),
    ('38', 'Review'),
    ('39', 'Screenplay'),
    ('40', 'Set photo'),
    ('41', 'Shot report'),
    ('42', 'Slide'),
    ('43', 'Story board'),
    ('44', 'Title list'),
    ('45', 'Typoscript'),
    ('46', 'Unclassified photo'),
    ('47', 'Press material')
)

# FORM is type used for IMC list
# example <keywords type="Form" lang="EN"> <term>Newsreel</term>  </keywords>
FORM = (
    ('01', 'Advertising film'),
    ('02', 'Amateur film'),
    ('03', 'Animated film'),
    ('04', 'Compilation'),
    ('05', 'Documentary'),
    ('06', 'Educational film'),
    ('07', 'Experimental film'),
    ('08', 'Feature film'),
    ('09', 'Loop'),
    ('10', 'Music video'),
    ('11', 'Newsreel'),
    ('12', 'Outtake'),
    ('13', 'Serial'),
    ('14', 'Series'),
    ('15', 'Short film'),
    ('16', 'Trailer'),
    ('17', 'TV film'),
    ('18', 'TV play'),
    ('19', 'Video installation')
)

# ISO-639-1 LanguageCS
LANGUAGE = (
    ('aa',  'Afar'),
    ('ab',  'Abkhazian'),
    ('ae',  'Avestan'),
    ('af',  'Afrikaans'),
    ('ak',  'Akan'),
    ('am',  'Amharic'),
    ('an',  'Aragonese'),
    ('ar',  'Arabic'),
    ('as',  'Assamese'),
    ('av',  'Avaric'),
    ('ay',  'Aymara'),
    ('az',  'Azerbaijani'),
    ('ba',  'Bashkir'),
    ('be',  'Belarusian'),
    ('bg',  'Bulgarian'),
    ('bh',  'Bihari'),
    ('bi',  'Bislama'),
    ('bm',  'Bambara'),
    ('bn',  'Bengali'),
    ('bo',  'Tibetan'),
    ('br',  'Breton'),
    ('bs',  'Bosnian'),
    ('ca',  'Catalan'),
    ('ce',  'Chechen'),
    ('ch',  'Chamorro'),
    ('co',  'Corsican'),
    ('cr',  'Cree'),
    ('cs',  'Czech'),
    ('cu',  'Church Slavic'),
    ('cv',  'Chuvash'),
    ('cy',  'Welsh'),
    ('da',  'Danish'),
    ('de',  'German'),
    ('dv',  'Divehi'),
    ('dz',  'Dzongkha'),
    ('ee',  'Ewe'),
    ('el',  'Greek'),
    ('en',  'English'),
    ('eo',  'Esperanto'),
    ('es',  'Spanish'),
    ('et',  'Estonian'),
    ('eu',  'Basque'),
    ('fa',  'Persian'),
    ('ff',  'Fulah'),
    ('fi',  'Finnish'),
    ('fj',  'Fijian'),
    ('fo',  'Faroese'),
    ('fr',  'French'),
    ('fy',  'Western Frisian'),
    ('ga',  'Irish'),
    ('gd',  'Scottish Gaelic'),
    ('gl',  'Galician'),
    ('gn',  'Guaraní'),
    ('gu',  'Gujarati'),
    ('gv',  'Manx'),
    ('ha',  'Hausa'),
    ('he',  'Hebrew'),
    ('hi',  'Hindi'),
    ('ho',  'Hiri Motu'),
    ('hr',  'Croatian'),
    ('ht',  'Haitian'),
    ('hu',  'Hungarian'),
    ('hy',  'Armenian'),
    ('hz',  'Herero'),
    ('ia',  'Interlingua (International Auxiliary Language Association)'),
    ('id',  'Indonesian'),
    ('ie',  'Interlingue'),
    ('ig',  'Igbo'),
    ('ii',  'Sichuan Yi'),
    ('ik',  'Inupiaq'),
    ('io',  'Ido'),
    ('is',  'Icelandic'),
    ('it',  'Italian'),
    ('iu',  'Inuktitut'),
    ('ja',  'Japanese'),
    ('jv',  'Javanese'),
    ('ka',  'Georgian'),
    ('kg',  'Kongo'),
    ('ki',  'Kikuyu'),
    ('kj',  'Kwanyama'),
    ('kk',  'Kazakh'),
    ('kl',  'Kalaallisut'),
    ('km',  'Khmer'),
    ('kn',  'Kannada'),
    ('ko',  'Korean'),
    ('kr',  'Kanuri'),
    ('ks',  'Kashmiri'),
    ('ku',  'Kurdish'),
    ('kv',  'Komi'),
    ('kw',  'Cornish'),
    ('ky',  'Kirghiz'),
    ('la',  'Latin'),
    ('lb',  'Luxembourgish'),
    ('lg',  'Ganda'),
    ('li',  'Limburgish'),
    ('ln',  'Lingala'),
    ('lo',  'Lao'),
    ('lt',  'Lithuanian'),
    ('lu',  'Luba-Katanga'),
    ('lv',  'Latvian'),
    ('mg',  'Malagasy'),
    ('mh',  'Marshallese'),
    ('mi',  'Māori'),
    ('mk',  'Macedonian'),
    ('ml',  'Malayalam'),
    ('mn',  'Mongolian'),
    ('mr',  'Marathi'),
    ('ms',  'Malay'),
    ('mt',  'Maltese'),
    ('my',  'Burmese'),
    ('na',  'Nauru'),
    ('nb',  'Norwegian Bokmål'),
    ('nd',  'North Ndebele'),
    ('ne',  'Nepali'),
    ('ng',  'Ndonga'),
    ('nl',  'Dutch'),
    ('nn',  'Norwegian Nynorsk'),
    ('no',  'Norwegian'),
    ('nr',  'South Ndebele'),
    ('nv',  'Navajo'),
    ('ny',  'Chichewa'),
    ('oc',  'Occitan'),
    ('oj',  'Ojibwa'),
    ('om',  'Oromo'),
    ('or',  'Oriya'),
    ('os',  'Ossetian'),
    ('pa',  'Panjabi'),
    ('pi',  'Pāli'),
    ('pl',  'Polish'),
    ('ps',  'Pashto'),
    ('pt',  'Portuguese'),
    ('qu',  'Quechua'),
    ('rm',  'Raeto-Romance'),
    ('rn',  'Kirundi'),
    ('ro',  'Romanian'),
    ('ru',  'Russian'),
    ('rw',  'Kinyarwanda'),
    ('sa',  'Sanskrit'),
    ('sc',  'Sardinian'),
    ('sd',  'Sindhi'),
    ('se',  'Northern Sami'),
    ('sg',  'Sango'),
    ('si',  'Sinhala'),
    ('sk',  'Slovak'),
    ('sl',  'Slovenian'),
    ('sm',  'Samoan'),
    ('sn',  'Shona'),
    ('so',  'Somali'),
    ('sq',  'Albanian'),
    ('sr',  'Serbian'),
    ('ss',  'Swati'),
    ('st',  'Southern Sotho'),
    ('su',  'Sundanese'),
    ('sv',  'Swedish'),
    ('sw',  'Swahili'),
    ('ta',  'Tamil'),
    ('te',  'Telugu'),
    ('tg',  'Tajik'),
    ('th',  'Thai'),
    ('ti',  'Tigrinya'),
    ('tk',  'Turkmen'),
    ('tl',  'Tagalog'),
    ('tn',  'Tswana'),
    ('to',  'Tonga'),
    ('tr',  'Turkish'),
    ('ts',  'Tsonga'),
    ('tt',  'Tatar'),
    ('tw',  'Twi'),
    ('ty',  'Tahitian'),
    ('ug',  'Uighur'),
    ('uk',  'Ukrainian'),
    ('ur',  'Urdu'),
    ('uz',  'Uzbek'),
    ('ve',  'Venda'),
    ('vi',  'Vietnamese'),
    ('vo',  'Volapük'),
    ('wa',  'Walloon'),
    ('wo',  'Wolof'),
    ('xh',  'Xhosa'),
    ('yi',  'Yiddish'),
    ('yo',  'Yoruba'),
    ('za',  'Zhuang'),
    ('zh',  'Chinese'),
    ('zu',  'Zulu'),
    ('ud',  'Undefined')
)

# ISO-639-2 LanguageCS
LANGUAGE_2 = (
    ('ace',     'Achinese'),
    ('ach',     'Acoli'),
    ('ada',     'Adangme'),
    ('ady',     'Adyghe; Adygei'),
    ('afa',     'Afro-Asiatic languages'),
    ('afh',     'Afrihili'),
    ('ain',     'Ainu'),
    ('akk',     'Akkadian'),
    ('ale',     'Aleut'),
    ('alg',     'Algonquian languages'),
    ('alt',     'Southern Altai'),
    ('ang',     'English, Old (ca.450-1100)'),
    ('anp',     'Angika'),
    ('apa',     'Apache languages'),
    ('arc',     'Official Aramaic (700-300 BCE); Imperial Aramaic (700-300 BCE)'),
    ('arn',     'Mapudungun; Mapuche'),
    ('arp',     'Arapaho'),
    ('art',     'Artificial languages'),
    ('arw',     'Arawak'),
    ('ast',     'Asturian; Bable; Leonese; Asturleonese'),
    ('ath',     'Athapascan languages'),
    ('aus',     'Australian languages'),
    ('awa',     'Awadhi'),
    ('bad',     'Banda languages'),
    ('bai',     'Bamileke languages'),
    ('bal',     'Baluchi'),
    ('ban',     'Balinese'),
    ('bas',     'Basa'),
    ('bat',     'Baltic languages'),
    ('bej',     'Beja; Bedawiyet'),
    ('bem',     'Bemba'),
    ('ber',     'Berber languages'),
    ('bho',     'Bhojpuri'),
    ('bih',     'Bihari languages'),
    ('bik',     'Bikol'),
    ('bin',     'Bini; Edo'),
    ('bla',     'Siksika'),
    ('bnt',     'Bantu languages'),
    ('bra',     'Braj'),
    ('btk',     'Batak languages'),
    ('bua',     'Buriat'),
    ('bug',     'Buginese'),
    ('byn',     'Blin; Bilin'),
    ('cad',     'Caddo'),
    ('cai',     'Central American Indian languages'),
    ('car',     'Galibi Carib'),
    ('cat',     'Catalan; Valencian'),
    ('cau',     'Caucasian languages'),
    ('ceb',     'Cebuano'),
    ('cel',     'Celtic languages'),
    ('chb',     'Chibcha'),
    ('chg',     'Chagatai'),
    ('chk',     'Chuukese'),
    ('chm',     'Mari'),
    ('chn',     'Chinook jargon'),
    ('cho',     'Choctaw'),
    ('chp',     'Chipewyan; Dene Suline'),
    ('chr',     'Cherokee'),
    ('chu',     'Church Slavic; Old Slavonic; Church Slavonic; Old Bulgarian; Old Church Slavonic'),
    ('chy',     'Cheyenne'),
    ('cmc',     'Chamic languages'),
    ('cop',     'Coptic'),
    ('cpe',     'Creoles and pidgins, English based'),
    ('cpf',     'Creoles and pidgins, French-based'),
    ('cpp',     'Creoles and pidgins, Portuguese-based'),
    ('crh',     'Crimean Tatar; Crimean Turkish'),
    ('crp',     'Creoles and pidgins'),
    ('csb',     'Kashubian'),
    ('cus',     'Cushitic languages'),
    ('dak',     'Dakota'),
    ('dar',     'Dargwa'),
    ('day',     'Land Dayak languages'),
    ('del',     'Delaware'),
    ('den',     'Slave (Athapascan)'),
    ('dgr',     'Dogrib'),
    ('din',     'Dinka'),
    ('div',     'Divehi; Dhivehi; Maldivian'),
    ('doi',     'Dogri'),
    ('dra',     'Dravidian languages'),
    ('dsb',     'Lower Sorbian'),
    ('dua',     'Duala'),
    ('dum',     'Dutch, Middle (ca.1050-1350)'),
    ('dyu',     'Dyula'),
    ('efi',     'Efik'),
    ('egy',     'Egyptian (Ancient)'),
    ('eka',     'Ekajuk'),
    ('elx',     'Elamite'),
    ('enm',     'English, Middle (1100-1500)'),
    ('ewo',     'Ewondo'),
    ('fan',     'Fang'),
    ('fat',     'Fanti'),
    ('fil',     'Filipino; Pilipino'),
    ('fiu',     'Finno-Ugrian languages'),
    ('fon',     'Fon'),
    ('frm',     'French, Middle (ca.1400-1600)'),
    ('fro',     'French, Old (842-ca.1400)'),
    ('frr',     'Northern Frisian'),
    ('frs',     'Eastern Frisian'),
    ('fur',     'Friulian'),
    ('gaa',     'Ga'),
    ('gay',     'Gayo'),
    ('gba',     'Gbaya'),
    ('gem',     'Germanic languages'),
    ('gez',     'Geez'),
    ('gil',     'Gilbertese'),
    ('gla',     'Gaelic; Scottish Gaelic'),
    ('gmh',     'German, Middle High (ca.1050-1500)'),
    ('goh',     'German, Old High (ca.750-1050)'),
    ('gon',     'Gondi'),
    ('gor',     'Gorontalo'),
    ('got',     'Gothic'),
    ('grb',     'Grebo'),
    ('grc',     'Greek, Ancient (to 1453)'),
    ('gre (B)', 'Greek, Modern (1453-)'),
    ('ell (T)', 'Greek, Modern (1453-)'),
    ('gsw',     'Swiss German; Alemannic; Alsatian'),
    ('gwi',     'Gwich in'),
    ('hai',     'Haida'),
    ('hat',     'Haitian; Haitian Creole'),
    ('haw',     'Hawaiian'),
    ('hil',     'Hiligaynon'),
    ('him',     'Himachali languages; Western Pahari languages'),
    ('hit',     'Hittite'),
    ('hmn',     'Hmong'),
    ('hsb',     'Upper Sorbian'),
    ('hup',     'Hupa'),
    ('iba',     'Iban'),
    ('iii',     'Sichuan Yi; Nuosu'),
    ('ijo',     'Ijo languages'),
    ('ile',     'Interlingue; Occidental'),
    ('ilo',     'Iloko'),
    ('inc',     'Indic languages'),
    ('ine',     'Indo-European languages'),
    ('inh',     'Ingush'),
    ('ira',     'Iranian languages'),
    ('iro',     'Iroquoian languages'),
    ('jbo',     'Lojban'),
    ('jpr',     'Judeo-Persian'),
    ('jrb',     'Judeo-Arabic'),
    ('kaa',     'Kara-Kalpak'),
    ('kab',     'Kabyle'),
    ('kac',     'Kachin; Jingpho'),
    ('kal',     'Kalaallisut; Greenlandic'),
    ('kam',     'Kamba'),
    ('kar',     'Karen languages'),
    ('kaw',     'Kawi'),
    ('kbd',     'Kabardian'),
    ('kha',     'Khasi'),
    ('khi',     'Khoisan languages'),
    ('khm',     'Central Khmer'),
    ('kho',     'Khotanese; Sakan'),
    ('kik',     'Kikuyu; Gikuyu'),
    ('kir',     'Kirghiz; Kyrgyz'),
    ('kmb',     'Kimbundu'),
    ('kok',     'Konkani'),
    ('kos',     'Kosraean'),
    ('kpe',     'Kpelle'),
    ('krc',     'Karachay-Balkar'),
    ('krl',     'Karelian'),
    ('kro',     'Kru languages'),
    ('kru',     'Kurukh'),
    ('kua',     'Kuanyama; Kwanyama'),
    ('kum',     'Kumyk'),
    ('kut',     'Kutenai'),
    ('lad',     'Ladino'),
    ('lah',     'Lahnda'),
    ('lam',     'Lamba'),
    ('lez',     'Lezghian'),
    ('lim',     'Limburgan; Limburger; Limburgish'),
    ('lol',     'Mongo'),
    ('loz',     'Lozi'),
    ('ltz',     'Luxembourgish; Letzeburgesch'),
    ('lua',     'Luba-Lulua'),
    ('lui',     'Luiseno'),
    ('lun',     'Lunda'),
    ('luo',     'Luo (Kenya and Tanzania)'),
    ('lus',     'Lushai'),
    ('mad',     'Madurese'),
    ('mag',     'Magahi'),
    ('mai',     'Maithili'),
    ('mak',     'Makasar'),
    ('man',     'Mandingo'),
    ('map',     'Austronesian languages'),
    ('mas',     'Masai'),
    ('mdf',     'Moksha'),
    ('mdr',     'Mandar'),
    ('men',     'Mende'),
    ('mga',     'Irish, Middle (900-1200)'),
    ('mic',     'Mi kmaq; Micmac'),
    ('min',     'Minangkabau'),
    ('mis',     'Uncoded languages'),
    ('mkh',     'Mon-Khmer languages'),
    ('mnc',     'Manchu'),
    ('mni',     'Manipuri'),
    ('mno',     'Manobo languages'),
    ('moh',     'Mohawk'),
    ('mos',     'Mossi'),
    ('mul',     'Multiple languages'),
    ('mun',     'Munda languages'),
    ('mus',     'Creek'),
    ('mwl',     'Mirandese'),
    ('mwr',     'Marwari'),
    ('myn',     'Mayan languages'),
    ('myv',     'Erzya'),
    ('nah',     'Nahuatl languages'),
    ('nai',     'North American Indian languages'),
    ('nap',     'Neapolitan'),
    ('nav',     'Navajo; Navaho'),
    ('nbl',     'Ndebele, South; South Ndebele'),
    ('nde',     'Ndebele, North; North Ndebele'),
    ('nds',     'Low German; Low Saxon; German, Low; Saxon, Low'),
    ('new',     'Nepal Bhasa; Newari'),
    ('nia',     'Nias'),
    ('nic',     'Niger-Kordofanian languages'),
    ('niu',     'Niuean'),
    ('dut (B)', 'Dutch; Flemish'),
    ('nld (T)', 'Dutch; Flemish'),
    ('nno',     'Norwegian Nynorsk; Nynorsk, Norwegian'),
    ('nob',     'Bokmål, Norwegian; Norwegian Bokmål'),
    ('nog',     'Nogai'),
    ('non',     'Norse, Old'),
    ('nqo',     'N Ko'),
    ('nso',     'Pedi; Sepedi; Northern Sotho'),
    ('nub',     'Nubian languages'),
    ('nwc',     'Classical Newari; Old Newari; Classical Nepal Bhasa'),
    ('nya',     'Chichewa; Chewa; Nyanja'),
    ('nym',     'Nyamwezi'),
    ('nyn',     'Nyankole'),
    ('nyo',     'Nyoro'),
    ('nzi',     'Nzima'),
    ('oci',     'Occitan (post 1500)'),
    ('osa',     'Osage'),
    ('oss',     'Ossetian; Ossetic'),
    ('ota',     'Turkish, Ottoman (1500-1928)'),
    ('oto',     'Otomian languages'),
    ('paa',     'Papuan languages'),
    ('pag',     'Pangasinan'),
    ('pal',     'Pahlavi'),
    ('pam',     'Pampanga; Kapampangan'),
    ('pan',     'Panjabi; Punjabi'),
    ('pap',     'Papiamento'),
    ('pau',     'Palauan'),
    ('peo',     'Persian, Old (ca.600-400 B.C.)'),
    ('phi',     'Philippine languages'),
    ('phn',     'Phoenician'),
    ('pon',     'Pohnpeian'),
    ('pra',     'Prakrit languages'),
    ('pro',     'Provençal, Old (to 1500);Occitan, Old (to 1500)'),
    ('pus',     'Pushto; Pashto'),
    ('qaa-qtz', 'Reserved for local use'),
    ('raj',     'Rajasthani'),
    ('rap',     'Rapanui'),
    ('rar',     'Rarotongan; Cook Islands Maori'),
    ('roa',     'Romance languages'),
    ('roh',     'Romansh'),
    ('rom',     'Romany'),
    ('rum (B)', 'Romanian; Moldavian; Moldovan'),
    ('ron (T)', 'Romanian; Moldavian; Moldovan'),
    ('run',     'Rundi'),
    ('rup',     'Aromanian; Arumanian; Macedo-Romanian'),
    ('sad',     'Sandawe'),
    ('sah',     'Yakut'),
    ('sai',     'South American Indian languages'),
    ('sal',     'Salishan languages'),
    ('sam',     'Samaritan Aramaic'),
    ('sas',     'Sasak'),
    ('sat',     'Santali'),
    ('scn',     'Sicilian'),
    ('sco',     'Scots'),
    ('sel',     'Selkup'),
    ('sem',     'Semitic languages'),
    ('sga',     'Irish, Old (to 900)'),
    ('sgn',     'Sign Languages'),
    ('shn',     'Shan'),
    ('sid',     'Sidamo'),
    ('sin',     'Sinhala; Sinhalese'),
    ('sio',     'Siouan languages'),
    ('sit',     'Sino-Tibetan languages'),
    ('sla',     'Slavic languages'),
    ('sma',     'Southern Sami'),
    ('smi',     'Sami languages'),
    ('smj',     'Lule Sami'),
    ('smn',     'Inari Sami'),
    ('sms',     'Skolt Sami'),
    ('snk',     'Soninke'),
    ('sog',     'Sogdian'),
    ('son',     'Songhai languages'),
    ('sot',     'Sotho, Southern'),
    ('spa',     'Spanish; Castilian'),
    ('srn',     'Sranan Tongo'),
    ('srr',     'Serer'),
    ('ssa',     'Nilo-Saharan languages'),
    ('suk',     'Sukuma'),
    ('sus',     'Susu'),
    ('sux',     'Sumerian'),
    ('syc',     'Classical Syriac'),
    ('syr',     'Syriac'),
    ('tai',     'Tai languages'),
    ('tem',     'Timne'),
    ('ter',     'Tereno'),
    ('tet',     'Tetum'),
    ('tig',     'Tigre'),
    ('tiv',     'Tiv'),
    ('tkl',     'Tokelau'),
    ('tlh',     'Klingon; tlhIngan-Hol'),
    ('tli',     'Tlingit'),
    ('tmh',     'Tamashek'),
    ('tog',     'Tonga (Nyasa)'),
    ('ton',     'Tonga (Tonga Islands)'),
    ('tpi',     'Tok Pisin'),
    ('tsi',     'Tsimshian'),
    ('tum',     'Tumbuka'),
    ('tup',     'Tupi languages'),
    ('tut',     'Altaic languages'),
    ('tvl',     'Tuvalu'),
    ('tyv',     'Tuvinian'),
    ('udm',     'Udmurt'),
    ('uga',     'Ugaritic'),
    ('uig',     'Uighur; Uyghur'),
    ('umb',     'Umbundu'),
    ('und',     'Undetermined'),
    ('vai',     'Vai'),
    ('vot',     'Votic'),
    ('wak',     'Wakashan languages'),
    ('wal',     'Wolaitta; Wolaytta'),
    ('war',     'Waray'),
    ('was',     'Washo'),
    ('wen',     'Sorbian languages'),
    ('xal',     'Kalmyk; Oirat'),
    ('yao',     'Yao'),
    ('yap',     'Yapese'),
    ('ypk',     'Yupik languages'),
    ('zap',     'Zapotec'),
    ('zbl',     'Blissymbols; Blissymbolics; Bliss'),
    ('zen',     'Zenaga'),
    ('zha',     'Zhuang; Chuang'),
    ('znd',     'Zande languages'),
    ('zun',     'Zuni'),
    ('zxx',     'No linguistic content; Not applicable'),
    ('zza',     'Zaza; Dimili; Dimli; Kirdki; Kirmanjki; Zazaki')
)

# FIXME
# COUNTRY_OF_REFERENCE = (
#     ('Country of production',   'Country of production'),
#     ('n/a',                     'n/a')
# )

# the following codelist is for CountryOfReference and Country and
# regionOfActivity: XPZ44-002HistoricCountryCS
COUNTRY = (
    ('AD',  'Andorra'),
    ('AE',  'United Arab Emirates'),
    ('AF',  'Afghanistan'),
    ('AG',  'Antigua and Barbuda'),
    ('AI',  'Anguilla'),
    ('AL',  'Albania'),
    ('AM',  'Armenia'),
    ('AO',  'Angola'),
    ('AQ',  'Antarctica'),
    ('AR',  'Argentina'),
    ('AS',  'American Samoa'),
    ('AT',  'Austria'),
    ('AU',  'Australia'),
    ('AW',  'Aruba'),
    ('AX',  'Aland Islands'),
    ('AZ',  'Azerbaijan'),
    ('BA',  'Bosnia and Herzegovina'),
    ('BB',  'Barbados'),
    ('BD',  'Bangladesh'),
    ('BE',  'Belgium'),
    ('BF',  'Burkina Faso'),
    ('BG',  'Bulgaria'),
    ('BH',  'Bahrain'),
    ('BI',  'Burundi'),
    ('BJ',  'Benin'),
    ('BL',  'Saint Barthélemy'),
    ('BM',  'Bermuda'),
    ('BN',  'Brunei Darussalam'),
    ('BO',  'Bolivia, Plurinational State of'),
    ('BR',  'Brazil'),
    ('BS',  'Bahamas'),
    ('BT',  'Bhutan'),
    ('BV',  'Bouvet Island'),
    ('BW',  'Botswana'),
    ('BY',  'Belarus'),
    ('BZ',  'Belize'),
    ('CA',  'Canada'),
    ('CC',  'Cocos (Keeling) Islands'),
    ('CD',  'Congo, the Democratic Republic of the'),
    ('CF',  'Central African Republic'),
    ('CG',  'Congo'),
    ('CH',  'Switzerland'),
    ('CI',  'Cote d\'Ivoire'),
    ('CK',  'Cook Islands'),
    ('CL',  'Chile'),
    ('CM',  'Cameroon'),
    ('CN',  'China'),
    ('CO',  'Colombia'),
    ('CR',  'Costa Rica'),
    ('CU',  'Cuba'),
    ('CV',  'Cape Verde'),
    ('CX',  'Christmas Island'),
    ('CY',  'Cyprus'),
    ('CZ',  'Czech Republic'),
    ('DE',  'Germany'),
    ('DJ',  'Djibouti'),
    ('DK',  'Denmark'),
    ('DM',  'Dominica'),
    ('DO',  'Dominican Republic'),
    ('DZ',  'Algeria'),
    ('EC',  'Ecuador'),
    ('EE',  'Estonia'),
    ('EG',  'Egypt'),
    ('EH',  'Western Sahara'),
    ('ER',  'Eritrea'),
    ('ES',  'Spain'),
    ('ET',  'Ethiopia'),
    ('FI',  'Finland'),
    ('FJ',  'Fiji'),
    ('FK',  'Falkland Islands (Malvinas)'),
    ('FM',  'Micronesia, Federated States of'),
    ('FO',  'Faroe Islands'),
    ('FR',  'France'),
    ('GA',  'Gabon'),
    ('GB',  'United Kingdom'),
    ('GD',  'Grenada'),
    ('GE',  'Georgia'),
    ('GF',  'French Guiana'),
    ('GG',  'Guernsey'),
    ('GH',  'Ghana'),
    ('GI',  'Gibraltar'),
    ('GL',  'Greenland'),
    ('GM',  'Gambia'),
    ('GN',  'Guinea'),
    ('GP',  'Guadeloupe'),
    ('GQ',  'Equatorial Guinea'),
    ('GR',  'Greece'),
    ('GS',  'South Georgia and the South Sandwich Islands'),
    ('GT',  'Guatemala'),
    ('GU',  'Guam'),
    ('GW',  'Guinea-Bissau'),
    ('GY',  'Guyana'),
    ('HK',  'Hong Kong'),
    ('HM',  'Heard Island and McDonald Islands'),
    ('HN',  'Honduras'),
    ('HR',  'Croatia'),
    ('HT',  'Haiti'),
    ('HU',  'Hungary'),
    ('ID',  'Indonesia'),
    ('IE',  'Ireland'),
    ('IL',  'Israel'),
    ('IM',  'Isle of Man'),
    ('IN',  'India'),
    ('IO',  'British Indian Ocean Territory'),
    ('IQ',  'Iraq'),
    ('IR',  'Iran, Islamic Republic of'),
    ('IS',  'Iceland'),
    ('IT',  'Italy'),
    ('JE',  'Jersey'),
    ('JM',  'Jamaica'),
    ('JO',  'Jordan'),
    ('JP',  'Japan'),
    ('KE',  'Kenya'),
    ('KG',  'Kyrgyzstan'),
    ('KH',  'Cambodia'),
    ('KI',  'Kiribati'),
    ('KM',  'Comoros'),
    ('KN',  'Saint Kitts and Nevis'),
    ('KP',  'Korea, Democratic People\'s Republic of'),
    ('KR',  'Korea, Republic of'),
    ('KW',  'Kuwait'),
    ('KY',  'Cayman Islands'),
    ('KZ',  'Kazakhstan'),
    ('LA',  'Lao People\'s Democratic Republic'),
    ('LB',  'Lebanon'),
    ('LC',  'Saint Lucia'),
    ('LI',  'Liechtenstein'),
    ('LK',  'Sri Lanka'),
    ('LR',  'Liberia'),
    ('LS',  'Lesotho'),
    ('LT',  'Lithuania'),
    ('LU',  'Luxembourg'),
    ('LV',  'Latvia'),
    ('LY',  'Libyan Arab Jamahiriya'),
    ('MA',  'Morocco'),
    ('MC',  'Monaco'),
    ('MD',  'Moldova, Republic of'),
    ('ME',  'Montenegro'),
    ('MF',  'Saint Martin (French part)'),
    ('MG',  'Madagascar'),
    ('MH',  'Marshall Islands'),
    ('MK',  'Macedonia, the former Yugoslav Republic of'),
    ('ML',  'Mali'),
    ('MM',  'Myanmar'),
    ('MN',  'Mongolia'),
    ('MO',  'Macao'),
    ('MP',  'Northern Mariana Islands'),
    ('MQ',  'Martinique'),
    ('MR',  'Mauritania'),
    ('MS',  'Montserrat'),
    ('MT',  'Malta'),
    ('MU',  'Mauritius'),
    ('MV',  'Maldives'),
    ('MW',  'Malawi'),
    ('MX',  'Mexico'),
    ('MY',  'Malaysia'),
    ('MZ',  'Mozambique'),
    ('NA',  'Namibia'),
    ('NC',  'New Caledonia'),
    ('NE',  'Niger'),
    ('NF',  'Norfolk Island'),
    ('NG',  'Nigeria'),
    ('NI',  'Nicaragua'),
    ('NL',  'Netherlands'),
    ('NO',  'Norway'),
    ('NP',  'Nepal'),
    ('NR',  'Nauru'),
    ('NU',  'Niue'),
    ('NZ',  'New Zealand'),
    ('OM',  'Oman'),
    ('PA',  'Panama'),
    ('PE',  'Peru'),
    ('PF',  'French Polynesia'),
    ('PG',  'Papua New Guinea'),
    ('PH',  'Philippines'),
    ('PK',  'Pakistan'),
    ('PL',  'Poland'),
    ('PM',  'Saint Pierre and Miquelon'),
    ('PN',  'Pitcairn'),
    ('PR',  'Puerto Rico'),
    ('PS',  'Palestinian Territory, Occupied'),
    ('PT',  'Portugal'),
    ('PW',  'Palau'),
    ('PY',  'Paraguay'),
    ('QA',  'Qatar'),
    ('RE',  'Reunion﻿Réunion'),
    ('RO',  'Romania'),
    ('RS',  'Serbia'),
    ('RU',  'Russian Federation'),
    ('RW',  'Rwanda'),
    ('SA',  'Saudi Arabia'),
    ('SB',  'Solomon Islands'),
    ('SC',  'Seychelles'),
    ('SD',  'Sudan'),
    ('SE',  'Sweden'),
    ('SG',  'Singapore'),
    ('SH',  'Saint Helena'),
    ('SI',  'Slovenia'),
    ('SJ',  'Svalbard and Jan Mayen'),
    ('SK',  'Slovakia'),
    ('SL',  'Sierra Leone'),
    ('SM',  'San Marino'),
    ('SN',  'Senegal'),
    ('SO',  'Somalia'),
    ('SR',  'Suriname'),
    ('ST',  'Sao Tome and Principe'),
    ('SV',  'El Salvador'),
    ('SY',  'Syrian Arab Republic'),
    ('SZ',  'Swaziland'),
    ('TC',  'Turks and Caicos Islands'),
    ('TD',  'Chad'),
    ('TF',  'French Southern Territories'),
    ('TG',  'Togo'),
    ('TH',  'Thailand'),
    ('TJ',  'Tajikistan'),
    ('TK',  'Tokelau'),
    ('TL',  'Timor-Leste'),
    ('TM',  'Turkmenistan'),
    ('TN',  'Tunisia'),
    ('TO',  'Tonga'),
    ('TR',  'Turkey'),
    ('TT',  'Trinidad and Tobago'),
    ('TV',  'Tuvalu'),
    ('TW',  'Taiwan, Province of China'),
    ('TZ',  'Tanzania, United Republic of'),
    ('UA',  'Ukraine'),
    ('UG',  'Uganda'),
    ('UM',  'United States Minor Outlying Islands'),
    ('US',  'United States'),
    ('UY',  'Uruguay'),
    ('UZ',  'Uzbekistan'),
    ('VA',  'Holy See (Vatican City State)'),
    ('VC',  'Saint Vincent and the Grenadines'),
    ('VE',  'Venezuela, Bolivarian Republic of'),
    ('VG',  'VirginIslands, British'),
    ('VI',  'VirginIslands, U.S.'),
    ('VN',  'Viet Nam'),
    ('VU',  'Vanuatu'),
    ('WF',  'Wallis and Futuna'),
    ('WS',  'Samoa'),
    ('YE',  'Yemen'),
    ('YT',  'Mayotte'),
    ('ZA',  'South Africa'),
    ('ZM',  'Zambia'),
    ('ZW',  'Zimbabwe')
)

# from EFG datalist
OBJECT_DATA_TYPE = (
    ('Issued',  'Issued'),
    ('Digitised',   'Digitised'),
    ('n/a',         'n/a')
)

# from EFG datalist
P_DATE_TYPE = (
    ('Date of birth'),              ('Date of birth'),
    ('Date of death'),              ('Date of death'),
    ('Year of activity(begin)'),    ('Year of activity(begin)'),
    ('Year of activity(end)'),      ('Year of activity(end)')
)

# MARC21_GeoAreasCS
# COUNTRY_OF_REFERENCE = (
# )
