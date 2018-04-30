import {Component, Input} from '@angular/core';
import {AppMediaModal} from "../app-media-modal";
import {AppShotsService} from "../../../../services/app-shots";
import {AppModaleService} from "../../../../services/app-modale";
import {AppVideoService} from "../../../../services/app-video";

@Component({
    selector: 'app-modal-insert-note',
    templateUrl: 'app-modal-insert-note.html'
})

export class AppModalInsertNoteComponent {

    @Input() data;

    constructor () {}

    save () {
        console.log("save",  this);
    }
}