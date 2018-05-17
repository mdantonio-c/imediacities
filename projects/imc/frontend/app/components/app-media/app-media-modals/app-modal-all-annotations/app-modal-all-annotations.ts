import {Component, OnInit, Input} from '@angular/core';

@Component({
    selector: 'app-modal-all-annotations',
    templateUrl: 'app-modal-all-annotations.html'
})

export class AppModalAllAnnotationsComponent implements OnInit {

    @Input() data;

    constructor() {
    }

    ngOnInit() {
    }
}