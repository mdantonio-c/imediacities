import {Component, Input, OnInit, ViewChild} from '@angular/core';
import {AppModaleService} from "../../services/app-modale";

@Component({
    selector: 'app-modale',
    templateUrl: 'app-modale.html'
})

export class AppModaleComponent {

    @ViewChild('content') content;

    titolo = '';

    constructor (private ModalService: AppModaleService) {}

    open (title, mediaType) {
        this.title_set(title);
        this.ModalService.open(this.content,{windowClass:`imc--modal page-type-${mediaType}`})
    }

    title_set (title) {
        this.titolo = title;
    }

}