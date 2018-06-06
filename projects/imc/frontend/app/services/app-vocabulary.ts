import {Injectable} from '@angular/core';
import {HttpClient} from '@angular/common/http';

@Injectable()
export class AppVocabularyService {

    _vocabolario = null;

    constructor(private http: HttpClient) {
    }

    get (cb) {

        if (!cb || typeof cb !== 'function') {
            console.log("AppVocabularyService", "Callback mancante");
            return
        }

        if (this._vocabolario) {
            cb(this._vocabolario_init());

        }else {

            this.http.get('/static/assets/vocabulary/vocabulary.json')
                .subscribe(
                    response => {

                        this._vocabolario = response;
                        cb(this._vocabolario_init());

                    },
                    err => {
                        console.log('Vocabolario non trovato!', err);
                    }
                )
        }
    }

    private _vocabolario_init () {
        this._vocabolario.terms.forEach(t => {
            this._vocabolario_reset(t);
        });
        return this._vocabolario;
    }

    private _vocabolario_reset (term) {
        term.open = false;
        if (term.hasOwnProperty('children')) {
            term.children.forEach(c => {
                c.open = false;
                c.selected = false;
                this._vocabolario_reset(c);
            })
        }
    }

    search (search_key) {

        let filtro = [];
        let search_re = new RegExp( search_key, 'gi' );

        let ricerca = (terms, search_key) => {

            terms.forEach(t => {

                if (t.hasOwnProperty('children')) {
                    ricerca(t.children, search_key);
                } else {
                    if (search_re.test(t.label)) {
                        filtro.push(
                            this.annotation_create(t)
                        )
                    }
                }

            })
        };

        ricerca(this._vocabolario.terms, search_key);
        return filtro;

    }

    annotation_create (term, group = 'term') {
        return {
            group: group,
            creator_type: 'user',
            name: term.label || term.name,
            iri: term.id || term.iri || null
        }
    }

    toggle_term(term, node = null) {
        if (!node) {
            node = { children: this._vocabolario.terms }
        }
        if (node.hasOwnProperty('children')) {
            node.children.forEach(c => {
                this.toggle_term(term, c);
            });
        } else {
            if (node.id === term.iri) {
                node.selected = !node.selected;
            }
        }
    }
}