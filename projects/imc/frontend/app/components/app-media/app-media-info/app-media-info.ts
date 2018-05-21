import {Component, Input, ViewChild, OnInit, AfterViewInit, ElementRef} from '@angular/core';

@Component({
    selector: 'app-media-info',
    templateUrl: 'app-media-info.html'
})

export class AppMediaInfoComponent implements AfterViewInit, OnInit {
    
    @Input() info: any;
    @Input() user_language: any;
    @ViewChild('description_languages_selector') description_languages_selector: ElementRef;

    public description_languages: any;
    public description_active = null;
    public isCollapsed = {
        title: true,
        description: false,
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
        this.description_active = user_language;
    }

    /**
     * Cicla le descrizioni per estrarne le lingue
     * se non è stata settata la lingua corrente la imposta alla prima
     * @param dati
     * @private
     */
    _descriptions_get_languages (dati) {
        dati.forEach(d => {
            if(!this.description_active) {
                this._user_language_set(d.attributes.language.key);
            }
            this.description_languages.set(d.attributes.language.key, d.attributes.language.description);
        });
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

    expandCard(card){
        this.isCollapsed[card] = !this.isCollapsed[card];
    }

    ngOnInit() {

        this.description_languages = new Map();

        if (this.user_language) {
            this._user_language_set(this.user_language);
        }

        this._descriptions_get_languages(this.info.relationships.descriptions);

        //  dato finto per simulare cambio lingua
        this.description_languages.set('xx','Lingua Fittizia per testare cambio lingua');



    }

    ngAfterViewInit () {

        if (this.description_languages.size > 1) {

            //  Imposto eventi
            this._description_languages_selector_events();

            //  Popolo opzioni per il select di cambio lingua
            this._description_languages_selector_set_options();

        }

    }
}