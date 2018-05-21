import {Component, OnInit, OnChanges, Input} from '@angular/core';

@Component({
    selector: 'app-modal-all-annotations',
    templateUrl: 'app-modal-all-annotations.html'
})

export class AppModalAllAnnotationsComponent implements OnInit, OnChanges {

    @Input() data;

    public shot;

    constructor() {
    }

    ngOnInit() {
        this.shot = this.data.shots[0];
    }

    ngOnChanges () {
        this.shot = this.data.shots[0];
    }
}