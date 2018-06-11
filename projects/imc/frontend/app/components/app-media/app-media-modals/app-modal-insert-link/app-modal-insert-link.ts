import {Component, OnInit, Input} from '@angular/core';

@Component({
    selector: 'app-modal-insert-link',
    templateUrl: 'app-modal-insert-link.html'
})

export class AppModalInsertLinkComponent implements OnInit {

    @Input() data;
    @Input() media_type: string;

    public options = true;

    optionsCheckbox = [
        {label: 'Video', checked: true},
        {label: 'Photo', checked: true},
        {label: 'Reference', checked: false},
        {label: 'Note', checked: false}
    ];

    constructor() {
    }

    ngOnInit() {
    }
}