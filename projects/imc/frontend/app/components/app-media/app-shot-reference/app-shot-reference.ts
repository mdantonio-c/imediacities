import {Component, Input, OnInit} from '@angular/core';

@Component({
    selector: 'app-shot-reference',
    templateUrl: 'app-shot-reference.html'
})

export class AppShotReferenceComponent implements OnInit {

    @Input() shot;

    constructor() {
    }

    ngOnInit() {
    }
}