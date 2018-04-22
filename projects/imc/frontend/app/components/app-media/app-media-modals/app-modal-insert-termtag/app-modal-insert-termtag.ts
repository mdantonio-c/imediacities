import {Component, OnInit, Input, AfterViewInit, ElementRef} from '@angular/core';
import {AppVideoService} from "../../../../services/app-video";
import {AppShotsService} from "../../../../services/app-shots";
import {HttpClient} from '@angular/common/http';

@Component({
    selector: 'app-modal-insert-termtag',
    templateUrl: 'app-modal-insert-termtag.html'
})

export class AppModalInsertTermtagComponent implements OnInit, AfterViewInit {

    @Input() data: any;

    mediaData = null;

    shots = null;
    shot_corrente = null;

    vocabolario = null;
    vocabolario_visualizza = false;

    terms = [];



    constructor(private http: HttpClient, private VideoService: AppVideoService, private ShotsService: AppShotsService, private elRef: ElementRef) {
        this.mediaData = this.VideoService.video();
        this.shots = this.ShotsService.shots();

        this.http.get('/static/assets/vocabulary/vocabulary.json')
            .subscribe(
                response => {
                    console.log("response",  response);
                    this.vocabolario = response;
                },
                err => {
                    console.log('Vocabolario non trovato!', err)
                }
            )

    }

    vocabolario_term (event) {
        let term = this.trova(event.target, 'li').children[1];
        let is_chiuso = term.classList.contains('display-none');
        //  Nascondo tutto
        this.nascondi(this.elRef.nativeElement.querySelectorAll('ul.term-list, ul.child-list'));
        //  Visualizzo
        if (is_chiuso){
            this.visualizza(term);
        }
    }

    vocabolario_child (event) {
        let child = this.trova(event.target, 'li' ).children[1];
        let is_chiuso = child.classList.contains('display-none');
        //  Nascondo
        this.nascondi(this.elRef.nativeElement.querySelectorAll('ul.child-list'));
        //  Visualizzo
        if (is_chiuso) {
            this.visualizza(child);
        }
    }

    vocabolario_leaf (term) {
        this.terms.push({
            group: 'term',
            creator_type: 'user',
            name: term.label,
            id: term.id
        });
    }

    trova (el, selector) {
        return el.closest(selector)
    }

    nascondi (elements) {
        for (let e = 0; e < elements.length; e++) {
            elements[e].classList.add('display-none');
        }
    }

    visualizza (element) {
        element.classList.remove('display-none');
    }

    ngAfterViewInit () {

        this.vocabolario_visualizza = true;

    }

    ngOnInit() {
        if (this.data.shots && this.data.shots.length) {
            this.shot_corrente = this.data.shots[0];
        }
    }
}