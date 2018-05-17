import {Component, Input, ViewChild, OnInit, AfterViewInit} from '@angular/core';

@Component({
    selector: 'app-media-annotation',
    templateUrl: 'app-media-annotation.html'
})

export class AppMediaAnnotationComponent implements OnInit, AfterViewInit {

    @Input() annotation;
    @ViewChild('badge') badge;

    constructor() {
    }

    ngOnInit() {
    }

    ngAfterViewInit () {
        let classe = 'badge-termtag';

        if (this.annotation.group === 'location') {
            classe = 'badge-geotag'
        }

        if (this.annotation.creator_type !== 'user') {
            classe += '--auto';
        }

        this.badge.nativeElement.classList.add(classe);

    }
}