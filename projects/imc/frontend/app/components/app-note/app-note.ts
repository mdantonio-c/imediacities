import {Component, HostBinding, Input, ElementRef, OnInit} from '@angular/core';
import {AppAnnotationsService} from "../../services/app-annotations";

@Component({
    selector: 'app-note',
    templateUrl: 'app-note.html'
})

export class AppNoteComponent implements OnInit {

    @HostBinding('class.notes') notes = true;
    @HostBinding('class.note-expanded') note_expanded = false;

    @Input() note;
    @Input() can_delete = false;

    public icon = 'keyboard_arrow_up';
    public popover;

    constructor(
        private element: ElementRef,
        private AnnotationsService: AppAnnotationsService
    ) {
    }

    delete () {
        if (!this.can_delete) return;
        if (this.note.id) {
            this.AnnotationsService.delete_tag(this.note, this.note.source);
        }

    }

    toggle () {
        this.icon = (this.icon === 'keyboard_arrow_up') ? 'keyboard_arrow_down' : 'keyboard_arrow_up';
        this.note_expanded = this.icon === 'keyboard_arrow_down';
    }

    ngOnInit() {
        this.popover = this.AnnotationsService.popover();
    }
}