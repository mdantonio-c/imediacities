import {Component, OnInit, OnChanges, Input} from '@angular/core';

@Component({
    selector: 'app-modal-lista-shots',
    templateUrl: 'app-modal-lista-shots.html'
})

export class AppModalListaShotsComponent implements OnInit, OnChanges {

    @Input() data: any;
    @Input() modal: boolean;
    @Input() cols: number;
    @Input() show_title: boolean;

    modal_class = '';
    col_class = '';

    constructor() {
    }

    ngOnInit() {}

    ngOnChanges () {

        if (this.modal) {
            this.modal_class = 'modal-body';
        }

        this.cols = this.cols || 2;
        this.col_class = 'col-' + (12/this.cols);

    }
}