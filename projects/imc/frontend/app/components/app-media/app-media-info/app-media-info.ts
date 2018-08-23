import {Component, Input, ViewChild, OnInit, AfterViewInit, ElementRef} from '@angular/core';

@Component({
    selector: 'app-media-info',
    templateUrl: 'app-media-info.html'
})

export class AppMediaInfoComponent implements AfterViewInit, OnInit {
    
    @Input() info: any;
    @Input() user_language: any;
    @ViewChild('description_languages_selector') description_languages_selector: ElementRef;
    @ViewChild('keyword_languages_selector') keyword_languages_selector: ElementRef;

    public description_languages: any;
    public description_active = null;
    public keyword_languages: any;
    public keyword_active = null;
    public isCollapsed = {
        title: true,
        description: false,
        keyword: true,
        prod_information: true,
        copyright: true,
        owner: true,
        analogue: true,
        format: true
    };

    constructor() {
    }

    /**
     * Imposta la lingua corrente
     * @param user_language
     * @private
     */
    _user_language_set (user_language) {
        //console.log('_user_language_set: user_language=' + JSON.stringify(user_language));
        this.description_active = user_language;
        this.keyword_active = user_language;
    }

    /**
     * Cicla le descrizioni per estrarne le lingue
     * se non è stata settata la lingua corrente la imposta alla prima
     * @param dati
     * @private
     */
    _descriptions_get_languages (dati) {

        let force_user_language = true;
        dati.forEach(d => {
            if (!d.attributes.language) {
                // for missing language
                this.description_languages.set('n/a', 'n/a');
                return;
            }

            if (!this.description_active) {
                this._user_language_set(d.attributes.language.key);
            }

            if (force_user_language && d.attributes.language.key === this.description_active) {
                force_user_language = false;
            }

            this.description_languages.set(d.attributes.language.key, d.attributes.language.description);
            //console.log("_descriptions_get_languages: -3- description_languages="+JSON.stringify(this.description_languages));
        });

        if (force_user_language) {
            let lang =  dati[0].attributes.language ? dati[0].attributes.language.key : 'n/a';
            this._user_language_set(lang);
        }
            //console.log("_descriptions_get_languages: -3- description_languages="+JSON.stringify(this.description_languages));
    }

    /**
     * Cicla le keyword per estrarne le lingue
     * se non è stata settata la lingua corrente la imposta alla prima
     * @param dati
     * @private
     */
    _keywords_get_languages (dati) {
        let force_user_language = true;
        //console.log("_keywords_get_languages: dati="+JSON.stringify(dati));
        dati.forEach(d => {
            //console.log("_keywords_get_languages: d.attributes.language="+JSON.stringify(d.attributes.language));
            if (!d.attributes.language) {
                // for missing language
                this.keyword_languages.set('n/a', 'n/a');
                return;
            }
            //console.log("_keywords_get_languages: this.keyword_active="+JSON.stringify(this.keyword_active));
            if (!this.keyword_active) {
                this._user_language_set(d.attributes.language.key);
            }

            if (force_user_language && d.attributes.language.key === this.keyword_active) {
                force_user_language = false;
            }

            this.keyword_languages.set(d.attributes.language.key, d.attributes.language.description);
            //console.log("_keywords_get_languages: -1- keyword_languages="+JSON.stringify(this.keyword_languages));
        });
        //console.log("_keywords_get_languages: -2- keyword_languages="+JSON.stringify(this.keyword_languages));
        if (force_user_language) {
            let lang =  dati[0].attributes.language ? dati[0].attributes.language.key : 'n/a';
            this._user_language_set(lang);
        }
    }

    /**
     * Eventi per la gestione del cambio della lingua delle descrizioni
     * @private
     */
    _description_languages_selector_events () {

        //  Fermo propagazione evento in modo da non provocare l'attivazione dell'accordion al click sul selettore delle lingue
        this.description_languages_selector.nativeElement.onclick = function(e) {
            e.stopPropagation();
        };

        //  Evento sul change della lingua
        this.description_languages_selector.nativeElement.onchange = () => {
            this._user_language_set(this.description_languages_selector.nativeElement.value);
        };

    }
    /**
     * Eventi per la gestione del cambio della lingua delle keyword
     * @private
     */
    _keyword_languages_selector_events () {

        //  Fermo propagazione evento in modo da non provocare l'attivazione dell'accordion al click sul selettore delle lingue
        this.keyword_languages_selector.nativeElement.onclick = function(e) {
            e.stopPropagation();
        };

        //  Evento sul change della lingua
        this.keyword_languages_selector.nativeElement.onchange = () => {
            this._user_language_set(this.keyword_languages_selector.nativeElement.value);
        };

    }
    /**
     * Crea le opzioni per la gestione della lignua delle descrizioni
     * @private
     */
    _description_languages_selector_set_options () {

        this.description_languages.forEach((value, key, map) => {

            const option = document.createElement('option');
            option.innerText = value;
            option.value= key;
            option.selected = key === this.description_active;

            this.description_languages_selector.nativeElement.appendChild(option);
        })

    }
    /**
     * Crea le opzioni per la gestione della lignua delle keyword
     * @private
     */
    _keyword_languages_selector_set_options () {

        this.keyword_languages.forEach((value, key, map) => {

            const option = document.createElement('option');
            option.innerText = value;
            option.value= key;
            option.selected = key === this.keyword_active;

            this.keyword_languages_selector.nativeElement.appendChild(option);
        })

    }
    expandCard(card){
        this.isCollapsed[card] = !this.isCollapsed[card];
    }

    ngOnInit() {
        this.description_languages = new Map();
        this.keyword_languages = new Map();
        if (this.user_language) {
            this._user_language_set(this.user_language);
        }
        //console.log('ngOnInit: this.info=' + JSON.stringify(this.info));
        this._descriptions_get_languages(this.info.relationships.descriptions);
        this._keywords_get_languages(this.info.relationships.keywords);
    }

    ngAfterViewInit () {
        if (this.description_languages.size > 1) {
            //  Imposto eventi
            this._description_languages_selector_events();
            //  Popolo opzioni per il select di cambio lingua
            this._description_languages_selector_set_options();
        }
        if (this.keyword_languages.size > 1) {
            //  Imposto eventi
            this._keyword_languages_selector_events();
            //  Popolo opzioni per il select di cambio lingua
            this._keyword_languages_selector_set_options();
        }
    }
}