import {Component, Input, OnInit} from '@angular/core';
import {AppMediaModal} from "../app-media-modal";
import {AppShotsService} from "../../../../services/app-shots";
import {AppModaleService} from "../../../../services/app-modale";
import {AppVideoService} from "../../../../services/app-video";


@Component({
    selector: 'app-modal-insert-geotag',
    templateUrl: 'app-modal-insert-geotag.html'
})

export class AppModalInsertGeotagComponent {

    @Input() data;

    constructor () {}

    save () {
        console.log("save",  this);
    }

}