import { Component, Input, Output, EventEmitter } from '@angular/core';
import { AppAnnotationsService } from "../../../../services/app-annotations";
import { infoResult } from "../../../../decorators/app-info";

@Component({
    selector: 'app-modal-insert-note',
    templateUrl: 'app-modal-insert-note.html'
})

export class AppModalInsertNoteComponent {

    @Input() data;
    @Input() media_type: string;

    @Output() shots_update: EventEmitter<any> = new EventEmitter();
    @infoResult() save_result;

    public note = {
        title: '',
        text: '',
        private: true,
        language: 'en'
    };

    constructor(private AnnotationsService: AppAnnotationsService) { }

    save() {

        let n = {
            private: this.note.private,
            language: this.note.language,
            value: this.note.text
        };
        //console.log('note to send', n)

        this.AnnotationsService.create_note(
            this.data.shots.map(s => s.id),
            n,
            this.media_type,
            (err, r) => {

                if (err) {
                    this.save_result.show('error');
                }

                this.save_result.show('success', 'Note added successfully');
                this.shots_update.emit(r);
            }
        );
    }
}