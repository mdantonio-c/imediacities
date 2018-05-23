import {Component, OnInit, OnChanges, Input, AfterViewInit, ViewChild, ElementRef, Output, EventEmitter} from '@angular/core';
import {AppVocabularyService} from "../../../../services/app-vocabulary";
import {AppAnnotationsService} from "../../../../services/app-annotations";
import {Observable} from 'rxjs';
import {debounceTime, distinctUntilChanged, map} from 'rxjs/operators';

@Component({
    selector: 'app-modal-insert-termtag',
    templateUrl: 'app-modal-insert-termtag.html'
})

export class AppModalInsertTermtagComponent implements OnInit, OnChanges, AfterViewInit {

    @Input() data: any;

    ricerca_model;

    @ViewChild('search_field') search_field: ElementRef;

    @Output() shots_update: EventEmitter<any> = new EventEmitter();

    vocabolario = null;
    vocabolario_visualizza = false;

    embargo_enable = false;
    embargo_model;

    ricerca_risultati = [];
    ricerca_key = {
        name: ''
    };
    ricerca_nomatch = false;

    terms = [];
    terms_all = [];

    constructor(
        private VocabularyService: AppVocabularyService,
        private AnnotationsService: AppAnnotationsService
    ) {}

    /**
     * Gestione della visibilità delle termini (elementi con children) del vocabolario sul click
     * @param term
     * @param parent
     */
    vocabolario_term (term, parent = null) {

        let valore_da_assegnare = !term.open;
        this.vocabolario.terms.forEach(t => {t.open = false;});
        if(parent) {
            parent.open = true;
            if (parent.hasOwnProperty('children')) {
                parent.children.forEach(c => {c.open = false})
            }
        }
        term.open = valore_da_assegnare;

    }
    /**
     * Gesitione del click sulle foglie (elementi senza children) del vocabolario
     * @param term
     */
    vocabolario_leaf (term) {
        term.selected = !term.selected;

        if ( term.selected ) {
            this.terms.push(
                this.VocabularyService.annotation_create(term)
            );
        } else {
            //  rimuovo da elenco terms
            this.terms = this.terms.filter(t => t.name !== term.label)
        }
    }
    /**
     * funzione di ricerca typeahead
     * @param {<string>} text$
     * @returns {any}
     */
    search = (text$: Observable<string>) =>
        text$.pipe(
            debounceTime(300),
            distinctUntilChanged(),
            map(term => term === '' ? [] : this.VocabularyService.search(term))
        );
    /**
     * formattatore dei risultati typeahead
     * @param {{name: string}} result
     * @returns {string}
     */
    formatter = (result: {name: string}) => result.name;
    //  se tra i tag trovati esiste un termine uguale al termine di ricerca disabilita il pulsante
    term_add_disable () {
        return this.ricerca_key && this.ricerca_key.name && this.ricerca_risultati.filter(r => r.name.toLowerCase() === this.ricerca_key.name.toLowerCase()).length
    }
    /**
     * Aggiunge il termine all'elenco dei termini da salvare
     * @param event
     */
    term_add (event) {
        if (typeof event === 'string') {
            event = {name:event}
        }
        if (event && event.name) {
            //  prevengo duplicazioni
            if( this.terms.filter(t => t.name.toLowerCase() === event.name.toLowerCase()).length === 0){
                this.terms.push(
                    this.VocabularyService.annotation_create(event)
                );
            }

        }
    }
    /**
     * rimuove term dall'elenco dei termini
     * @param term
     */
    term_remove (term) {
        this.terms = this.terms.filter(t => t.name !== term.name);
    }

    /**
     * Una voce di ricerca viene cliccata
     * @param term
     */
    term_selected (term) {
        this.term_add(term.item);
    }
    /**
     * esegue il salvataggio
     */
    salva () {
        this.AnnotationsService.create_tag(
            this.data.shots.map(s => s.id),
            this.terms,
            (response) => {

                response.some(r => {
                    if (!r.errors) {
                        this.shots_update.emit(r.data);
                        return true;
                    }
                })

            }
        );
    }

    ngOnInit() {}

    ngOnChanges () {

        this.terms_all = this.AnnotationsService.merge(this.data.shots, 'tags');

        this.VocabularyService.get((vocabolario)=>{this.vocabolario = vocabolario});
        this.ricerca_model = this.data.shots;
        this.terms = [];
        this.ricerca_risultati = [];
        if (this.search_field) {
            this.search_field.nativeElement.value = '';
        }
    }

    ngAfterViewInit () {
        this.vocabolario_visualizza = true;
    }

}