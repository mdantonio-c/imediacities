import {Component, OnInit, OnChanges, Input, AfterViewInit, OnDestroy, ViewChild, ElementRef, Output, EventEmitter} from '@angular/core';
import {AppVocabularyService} from "../../../../services/app-vocabulary";
import {AppVideoPlayerComponent} from "../../app-video-player/app-video-player";
import {NgbActiveModal, NgbModal} from '@ng-bootstrap/ng-bootstrap';
import {AppAnnotationsService} from "../../../../services/app-annotations";

@Component({
    selector: 'app-modal-insert-termtag',
    templateUrl: 'app-modal-insert-termtag.html'
})

export class AppModalInsertTermtagComponent implements OnInit, OnChanges, AfterViewInit {

    @Input() data: any;

    @ViewChild('search_field') search_field: ElementRef;

    @Output() shots_update: EventEmitter<any> = new EventEmitter();

    vocabolario = null;
    vocabolario_visualizza = false;

    embargo_enable = false;

    ricerca_risultati = [];
    ricerca_key = {
        name: ''
    };
    ricerca_nomatch = false;

    terms = [];

    constructor(
        private VocabularyService: AppVocabularyService,
        private AnnotationsService: AppAnnotationsService
    ) {}

    vocabolario_term (term) {
        term.open = !term.open;

    }

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

    ricerca (event) {
        if(event.target.value.length >= 3) {
            this.ricerca_key = {name: event.target.value};
            this.ricerca_risultati = this.VocabularyService.search(event.target.value);
            this.ricerca_nomatch = this.ricerca_risultati.length == 0
        } else {
            this.ricerca_key = null;
            this.ricerca_nomatch = false;
        }
    }

    term_add_disable () {
        return this.ricerca_key && this.ricerca_key.name && this.ricerca_risultati.filter(r => r.name.toLowerCase() === this.ricerca_key.name.toLowerCase()).length
        //length == 1 && this.ricerca_key && this.ricerca_key.name.toLowerCase() === this.ricerca_risultati[0].name.toLowerCase()
    }

    term_add (event) {
        console.log("event",  event);
        if (event && event.name) {

            if( this.terms.filter(t => t.name.toLowerCase() === event.name.toLowerCase()).length === 0){
                this.terms.push(
                    this.VocabularyService.annotation_create(event)
                );
            }
            console.log("this.terms",  this.terms);
        }
    }

    salva () {
        this.AnnotationsService.create_tag(
            this.data.shots[0].id,
            this.terms,
            (r) => {this.shots_update.emit(r)}
        );
    }

    ngOnInit() {}

    ngOnChanges () {

        this.VocabularyService.get((vocabolario)=>{this.vocabolario = vocabolario});

        this.terms = [];
        this.ricerca_risultati = [];
        this.search_field.nativeElement.value = '';
    }

    ngAfterViewInit () {
        this.vocabolario_visualizza = true;
    }

}