# Specifiche di mapping EFG da formato excel

efgEntity

- avcreation
- nonavcreation

### avcreation

---

- [x] **identifier**\* (1)

```
 <identifier scheme="CP_CATEGORY_ID">CCB_avCreation_23463</identifier>
```

| identifier           |
| -------------------- |
| CCB_avCreation_23463 |

---

- [x] **recordSource**\* (1..N)

```
 <recordSource>
  <sourceID>23463</sourceID>
  <provider id="CCB" schemeID="Institution acronym">Cineteca di Bologna</provider>
 </recordSource>
```

| sourceID | provider            | provider_id |
| -------- | ------------------- | ----------- |
| 23463    | Cineteca di Bologna | CCB         |

In IMC viene mappata e gestita SOLO la prima occorrenza del composite `recordSource`.

---

- [ ] **title**\* (1..N)

```
 <title lang="it">
  <text>Viaggio in Emilia Romagna</text>
  <relation>Original title</relation>
 </title>
 <title lang="en">
  <text>Travel to Emilia Romagna</text>
  <relation>Translated title</relation>
 </title>
```

| title_text_it             | title_relation | title_text_en            | title_relation   |
| ------------------------- | -------------- | ------------------------ | ---------------- |
| Viaggio in Emilia Romagna | Original title | Travel to Emilia Romagna | Translated title |

`title_relation` è opzionale. Se presente deve comparire nella colonna subito a destra del `title_text`.

---

- [ ] **identifyingTitle** (1)

```
 <identifyingTitle>Viaggio in Emilia Romagna</identifyingTitle>
```

| identifyingTitle          |
| ------------------------- |
| Viaggio in Emilia Romagna |

Questo elemento può essere omesso e compilato con il primo `title_text`.

---

- [x] **language**\* (0..N)

Vengono mappati i valori in `avManifastation` o `nonAVManifestation`

---

- [x] **countryOfReference** (1..N)

```
 <countryOfReference>IT</countryOfReference>
```

| countryOfReference |
| ------------------ |
| IT                 |

Occorrenze multiple separate dal ";" (e.g. IT;EN)

---

- [x] **productionYear** (1..N)

```
 <productionYear>1972</productionYear>
```

| productionYear |
| -------------- |
| 1972           |

Occorrenze multiple separate dal ";"

---

- [ ] **keywords** (0..N) \*

```
 <keywords lang="en" scheme="Cineteca di Bologna" type="Form">
  <term>Documentary</term>
 </keywords>
 <keywords lang="en" type="Project">
  <term>IMediaCities</term>
 </keywords>
```

| keywords_Form  | keywords_Project |
| -------------- | ---------------- |
| Documentary:en | IMediaCities:en  |

Occorrenze multiple separate dal ";"

---

- [ ] **description** (0..N) \*
  - _type_ (0..1)
  - _lang_ (1)

```
 <description lang="it" type="Synopsis">....</description>
 <description lang="en" type="Synopsis">....</description>
```

| description_it    | description_en  |
| ----------------- | --------------- |
| testo in italiano | text in english |

Consentite occorrenze multiple su più colonne.  
L'attributo type non è al momento gestito. Viene ignorato e non mappato.

---

- [ ] **avManifestation** (1..N) [1]

```
 <avManifestation>...</avManifestation>
```

---

- [ ] **relPerson** (0..N)
  - identifier (1)
  - name (1)
  - type (0..1)

XML

```
 <relPerson>
  <identifier scheme="CP_CATEGORY_ID">CCB_person_5f9930a5fcd55e80af478e2811c61f33</identifier>
  <name>Mingozzi, Primo</name>
  <type>Director</type>
 </relPerson>
```

| relPerson                                                            |
| -------------------------------------------------------------------- |
| CCB_person_5f9930a5fcd55e80af478e2811c61f33:Mingozzi, Primo:Director |

nota: occorrenze multiple separate dal ";"

---

- [ ] **relCorporate** (0..N)
  - identifier (1)
  - name (1)
  - type (0..1)

```
 <relCorporate>
  <identifier scheme="CP_CATEGORY_ID">CCB_corporate_f0dc0710e8a804a2e05118c0596a8ca5</identifier>
  <name>Ufficio Stampa della Giunta Regione Emilia Romagna</name>
  <type>Production company</type>
 </relCorporate>
```

| relCorporate                                                                                                         |
| -------------------------------------------------------------------------------------------------------------------- |
| CCB_corporate_f0dc0710e8a804a2e05118c0596a8ca5:Ufficio Stampa della Giunta Regione Emilia Romagna:Production company |

nota: occorrenze multiple separate dal ";"

---

- [ ] **relCollection**\* (0..N)
- identifier (1)
- name (1)
- type (0..1)

Solo il primo elemento in IMC.

---

### avManifestation

---

- [ ] **identifier** (1)

---

- [ ] **recordSource** (1..N)

---

- [ ] **title** (0..N)

---

- [x] **language** (0..N)

```
 <language>it</language>
```

| language |
| -------- |
| it       |

Occorrenze multiple separate dal ";"

---

- [ ] **dimension** (0..N)

---

- [ ] **duration** (0..1)

---

- [x] **format** (0..1)
  - gauge (0..1)
  - aspectRatio (0..1)
  - colour (0..1)
  - sound (0..1)

```
 <format>
  <gauge>8 mm</gauge>
  <aspectRatio>1:1,33</aspectRatio>
  <colour>Black &amp; White</colour>
  <sound hasSound="false">Without sound</sound>
 </format>
```

| gauge | aspectRatio  | colour        | hasSound |
| ----- | ------------ | ------------- | -------- |
| 8 mm  | value:1:1,33 | Black & White | false    |

"&" non deve essere codificato come Character Entity (vale per tutti).  
Valori possibili per un booleano:

- "y", "yes", "t", "true", "on", "1", 1, =True()
- "n", "no", "f", "false", "off", "0", 0, =False()

---

- [ ] **rightsHolder** (0..N)

---

- [ ] **rightsStatus** (0..N)

---

- [x] **thumbnail** (1)

```
 <thumbnail>https://...</thumbnail>
```

| thumbnail   |
| ----------- |
| https://... |

---

- [x] item (0..N)
  - isShownAt (1)

```
 <item>
   <isShownAt>https://ms-emilia-romagna.homemovies.it/it/clip/78</isShownAt>
 </item>
```

| isShownAt                                          |
| -------------------------------------------------- |
| https://ms-emilia-romagna.homemovies.it/it/clip/78 |

L'unico in `item` elemento gestito in IMC è `isShownAt`

---

### nonavcreation
