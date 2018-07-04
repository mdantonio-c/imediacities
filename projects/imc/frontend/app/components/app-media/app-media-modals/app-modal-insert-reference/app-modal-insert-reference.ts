import {Component, OnInit, Input} from '@angular/core';

@Component({
    selector: 'app-modal-insert-reference',
    templateUrl: 'app-modal-insert-reference.html'
})

export class AppModalInsertReferenceComponent implements OnInit {

    @Input() data;
    @Input() media_type: string;

    constructor() {
    }

    ngOnInit() {
    }
}