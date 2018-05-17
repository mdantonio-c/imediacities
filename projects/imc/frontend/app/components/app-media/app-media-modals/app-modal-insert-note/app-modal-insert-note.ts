import {Component, Input, Output, EventEmitter} from '@angular/core';
// import {AppMediaModal} from "../app-media-modal";
// import {AppShotsService} from "../../../../services/app-shots";
// import {AppModaleService} from "../../../../services/app-modale";
// import {AppVideoService} from "../../../../services/app-video";
import {AppAnnotationsService} from "../../../../services/app-annotations";

@Component({
    selector: 'app-modal-insert-note',
    templateUrl: 'app-modal-insert-note.html'
})

export class AppModalInsertNoteComponent {

    @Input() data;

    @Output() shots_update: EventEmitter<any> = new EventEmitter();

    public note = {
        title: '',
        text: '',
        private: true,
        language: 'it'
    };

    constructor (private AnnotationsService: AppAnnotationsService) {}

    save () {
        console.log("save",  this.note);
        let n = {
            private: this.note.private,
            language: this.note.language,
            value: this.note.text
        };
        console.log("n",  n);
        this.AnnotationsService.create_note(this.data.shots[0].id, n, (r) => {this.shots_update.emit(r)});
    }
}