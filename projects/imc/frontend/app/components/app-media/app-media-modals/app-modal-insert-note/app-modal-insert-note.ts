import {Component, Input, Output, EventEmitter} from '@angular/core';
import {AppAnnotationsService} from "../../../../services/app-annotations";

@Component({
    selector: 'app-modal-insert-note',
    templateUrl: 'app-modal-insert-note.html'
})

export class AppModalInsertNoteComponent {

    @Input() data;
    @Input() media_type: string;

    @Output() shots_update: EventEmitter<any> = new EventEmitter();

    public note = {
        title: '',
        text: '',
        private: true,
        language: 'it'
    };

    constructor (private AnnotationsService: AppAnnotationsService) {}

    save () {

        let n = {
            private: this.note.private,
            language: this.note.language,
            value: this.note.text
        };

        this.AnnotationsService.create_note(
            this.data.shots.map(s => s.id),
            n,
            this.media_type,
            (r) => {this.shots_update.emit(r)}
        );
    }
}