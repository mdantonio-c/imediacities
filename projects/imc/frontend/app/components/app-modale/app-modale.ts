import { Component, ViewChild, OnInit } from '@angular/core';
import { AppModaleService } from "../../services/app-modale";

@Component({
    selector: 'app-modale',
    templateUrl: 'app-modale.html'
})

export class AppModaleComponent implements OnInit {

    @ViewChild('content') content;

    public titolo = '';

    constructor(private ModalService: AppModaleService) {
    }

    open(title, media_type, classi = '') {
        this.title_set(title);
        this.ModalService.open(this.content, { windowClass: `imc--modal page-type-${media_type} ${classi}` })
    }

    title_set(title) {
        this.titolo = title;
    }

    ngOnInit() { }

}