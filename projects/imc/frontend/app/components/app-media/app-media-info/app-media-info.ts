import { Component, Input, ViewChild, OnInit, AfterViewInit, ElementRef } from '@angular/core';
import { AuthService } from "@rapydo/services/auth";
import { AppMediaService } from "../../../services/app-media";
import { is_item_owner } from "../../../decorators/app-item-owner";

@Component({
    selector: 'app-media-info',
    templateUrl: 'app-media-info.html'
})

export class AppMediaInfoComponent implements AfterViewInit, OnInit {

    @Input() info: any;
    @Input() user_language: any;
    @ViewChild('description_languages_selector', { static: false }) description_languages_selector: ElementRef;
    @ViewChild('keyword_languages_selector', { static: false }) keyword_languages_selector: ElementRef;

    @is_item_owner() is_item_owner;

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
    item: any;
    user: any;

    constructor(private AuthService: AuthService,
                private MediaService: AppMediaService,) {
    }

    /**
     * Imposta la lingua della description
     * @param new_description_language
     * @private
     */
    _description_language_set(new_description_language) {
        this.description_active = new_description_language;
    }
    /**
     * Imposta la lingua della keyword
     * @param new_keyword_language
     * @private
     */
    _keyword_language_set(new_keyword_language) {
        this.keyword_active = new_keyword_language;
    }

    /**
     * Cicla le descrizioni per estrarne le lingue
     * se non è stata settata la lingua corrente la imposta alla prima
     * @param dati
     * @private
     */
    _descriptions_get_languages(dati) {

        let force_user_language = true;
        dati.forEach(d => {
            if (!d.attributes.language) {
                // for missing language
                this.description_languages.set('n/a', 'n/a');
                return;
            }

            if (!this.description_active) {
                this._description_language_set(d.attributes.language.key);
            }

            if (force_user_language && d.attributes.language.key === this.description_active) {
                force_user_language = false;
            }

            this.description_languages.set(d.attributes.language.key, d.attributes.language.description);
        });

        if (force_user_language) {
            let lang = dati[0].attributes.language ? dati[0].attributes.language.key : 'n/a';
            this._description_language_set(lang);
        }
    }

    /**
     * Cicla le keyword per estrarne le lingue
     * se non è stata settata la lingua corrente la imposta alla prima
     * @param dati
     * @private
     */
    _keywords_get_languages(dati) {
        let force_user_language = true;
        dati.forEach(d => {
            if (!d.attributes.language) {
                // for missing language
                this.keyword_languages.set('n/a', 'n/a');
                return;
            }
            if (!this.keyword_active) {
                this._keyword_language_set(d.attributes.language.key);
            }

            if (force_user_language && d.attributes.language.key === this.keyword_active) {
                force_user_language = false;
            }
            this.keyword_languages.set(d.attributes.language.key, d.attributes.language.description);
        });
        if (force_user_language) {
            let lang = dati[0].attributes.language ? dati[0].attributes.language.key : 'n/a';
            this._keyword_language_set(lang);
        }
    }

    /**
     * Eventi per la gestione del cambio della lingua delle descrizioni
     * @private
     */
    _description_languages_selector_events() {

        //  Fermo propagazione evento in modo da non provocare l'attivazione dell'accordion al click sul selettore delle lingue
        this.description_languages_selector.nativeElement.onclick = function(e) {
            e.stopPropagation();
        };

        //  Evento sul change della lingua
        this.description_languages_selector.nativeElement.onchange = () => {
            this._description_language_set(this.description_languages_selector.nativeElement.value);
        };

    }
    /**
     * Eventi per la gestione del cambio della lingua delle keyword
     * @private
     */
    _keyword_languages_selector_events() {

        //  Fermo propagazione evento in modo da non provocare l'attivazione dell'accordion al click sul selettore delle lingue
        this.keyword_languages_selector.nativeElement.onclick = function(e) {
            e.stopPropagation();
        };

        //  Evento sul change della lingua
        this.keyword_languages_selector.nativeElement.onchange = () => {
            this._keyword_language_set(this.keyword_languages_selector.nativeElement.value);
        };

    }
    /**
     * Crea le opzioni per la gestione della lignua delle descrizioni
     * @private
     */
    _description_languages_selector_set_options() {

        this.description_languages.forEach((value, key, map) => {

            const option = document.createElement('option');
            option.innerText = value;
            option.value = key;
            option.selected = key === this.description_active;

            this.description_languages_selector.nativeElement.appendChild(option);
        })

    }
    /**
     * Crea le opzioni per la gestione della lignua delle keyword
     * @private
     */
    _keyword_languages_selector_set_options() {

        this.keyword_languages.forEach((value, key, map) => {

            const option = document.createElement('option');
            option.innerText = value;
            option.value = key;
            option.selected = key === this.keyword_active;

            this.keyword_languages_selector.nativeElement.appendChild(option);
        })

    }

    expandCard(card) {
        this.isCollapsed[card] = !this.isCollapsed[card];
    }

    togglePublicAccess() {
        let newVal = !this.info.relationships.item[0].attributes.public_access;
        this.MediaService.updatePublicAccess(newVal);
    }

    printContainerInfo() {
        // from ffprobe in the following form: mov,mp4,m4a,3gp,3g2,mj2
        // as the item is always transcoded as mp4 look for mp4 in the list
        // or provide the first
        let containers = this.item.attributes.digital_format[0].split(',');
        return (containers.includes('mp4')) ? 'mp4' : containers[0].trim();
    }

    printEncodingInfo() {
       // from ffprobe in the following long name form: H.264 / AVC / MPEG-4 AVC / MPEG-4 part 10
       // always print the first value
       return this.item.attributes.digital_format[1].split('/')[0].trim();
    }

    ngOnInit() {
        this.user = this.AuthService.getUser();
        this.description_languages = new Map();
        this.keyword_languages = new Map();
        if (this.user_language) {
            this._description_language_set(this.user_language);
            this._keyword_language_set(this.user_language);
        }
        if (this.info.relationships.descriptions) {
            this._descriptions_get_languages(this.info.relationships.descriptions);
        }
        if (this.info.relationships.keywords) {
            this._keywords_get_languages(this.info.relationships.keywords);
        }
        if (this.info.relationships.item) {
            this.item = this.info.relationships.item[0].relationships.other_version ? 
                this.info.relationships.item[0].relationships.other_version[0] : this.info.relationships.item[0]
        }
    }

    ngAfterViewInit() {
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