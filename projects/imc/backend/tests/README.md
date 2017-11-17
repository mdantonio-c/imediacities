## Test delle REST APIs con pytest


### Prerequisiti per l'utilizzo dei test

Nel database devono già esistere almeno:
- un gruppo di test (cioè ricercabile con nome 'test')
- l'utente di default per potersi autenticare
- i seguenti Role: admin_root, Archive, Researcher

### Dove si trovano i file dei test delle REST APIs del backend

```
.../imediacity/projects/imc/backend/tests/
```

Nella sottodir 
```
data
```
si trovano i file necessari ai test: un video, un xml e un txt.


### Quali API sono coperte al momento
- admin_groups
- admin_users
- upload
- stage
- annotations
- shots
- videos
- search

Non sono implementati test per:
- bulk
- vocabulary


### Come lanciare i test

Dalla directory root del repository git:
```
.../imediacity/
```

lanciare:
```
rapydo start
```
che, essendo la modalità debug il default, tira su i vari container senza far ancora partire il backend e il frontend.

Lanciare poi:
```
rapydo shell backend
```
che apre una shell dentro il container backend, cioè mi trovo l'ambiente in cui girerà il backend, che al momento ancora non gira essendo modalità debug.

Lanciare poi:
```
restapi init
```
che inizializza il database con i dati minimi necessari ai test.

I test possono essere lanciati singolarmente:
```
py.test -s tests/custom/test_videos.py
```
oppure tutti i test custom:
```
py.test -s tests/custom
```
oppure anche i test di base:
```
py.test -s tests
```
Inoltre c'è anche il wrapper "restapi tests" che lancia i test e calcola il coverage.


Nel container è già installato il plugin pytest-coverage, quindi per calcolare la coverage 
aggiungere alla riga di comando l'opzione --cov
```
py.test -s --cov=imc.apis tests/custom/test_videos.py
```
perché vengano generati tutti i file di report del coverage usare questo comando
```
py.test -s --cov-report html:cov_html --cov-report xml:cov.xml --cov-report annotate:cov_annotate --cov=imc.apis tests/custom
```
