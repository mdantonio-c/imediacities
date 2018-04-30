
import {Component, OnInit, OnChanges, Input, AfterViewInit, OnDestroy, ViewChild, ElementRef} from '@angular/core';
import {AppVideoService} from "../../../../services/app-video";
import {AppShotsService} from "../../../../services/app-shots";
import {AppVocabularyService} from "../../../../services/app-vocabulary";

import {AppVideoPlayerComponent} from "../../app-video-player/app-video-player";

import {NgbActiveModal, NgbModal} from '@ng-bootstrap/ng-bootstrap';
import {AppModaleService} from "../../../../services/app-modale";


@Component({
    selector: 'app-modal-insert-termtag',
    templateUrl: 'app-modal-insert-termtag.html'
})

export class AppModalInsertTermtagComponent implements OnInit, OnChanges, AfterViewInit {

    @Input() data: any;

    @ViewChild('videoPlayer') videoPlayer: AppVideoPlayerComponent;
    @ViewChild('search_field') search_field: ElementRef;


    // mediaData = null;

    // shots = null;
    // shot_corrente = null;

    vocabolario = null;
    vocabolario_visualizza = false;

    ricerca_risultati = [];

    terms = [];

    constructor(
        private VocabularyService: AppVocabularyService,
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
            this.terms = this.terms.filter(t => t.name !== term.label)
        }
    }

    ricerca (event) {
        if(event.target.value.length >= 3) {
            this.ricerca_risultati = this.VocabularyService.search(event.target.value);
        }
    }

    salva () {
        //console.log("salva", this);
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