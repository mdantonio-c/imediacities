
## Prerequisiti per l'utilizzo dei test

Devono esistere almeno un gruppo di test (cioè con nome 'test') e un 
video (con il suo corrispondente item) nel database.


## Dove si trovano i file dei test delle rest apis del backend ##

.../imediacity/projects/imc/backend/tests/


## Quali API sono coperte al momento ##
admin_groups
admin_users
annotations
search
shots
stage
videos

Non sono implementati test per:
bulk
upload
vocabulary


## Come lanciare i test ##

Dalla directory root del repository git:
.../imediacity/

lanciare:
rapydo start
che, essendo la modalità debug il default, tira su i vari container senza far ancora partire il backend e il frontend.

Lanciare poi:
rapydo shell backend
che apre una shell dentro il container backend, cioè mi trovo l'ambiente in cui girerà il backend, che al momento ancora non gira essendo modalità debug.

I test possono essere lanciati singolarmente:
py.test -s tests/custom/test_videos.py

oppure tutti i test custom:
py.test -s tests/custom

oppure anche i test di base:
py.test -s tests

Inoltre c'è anche il wrapper "restapi tests" che lancia i test e calcola il coverage.


Nel container è già installato il plugin pytest-coverage, quindi per calcolare la coverage 
aggiungere alla riga di comando l'opzione --cov

py.test -s --cov=imc.apis tests/custom/test_videos.py


