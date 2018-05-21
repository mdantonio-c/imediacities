import {Component, ElementRef, Input, OnInit} from '@angular/core';
import {AppAnnotationsService} from "../../../services/app-annotations";

@Component({
    selector: 'app-media-annotation',
    templateUrl: 'app-media-annotation.html'
})

export class AppMediaAnnotationComponent implements OnInit {

    @Input() annotation;
    @Input() clickable;
    @Input() can_delete;

    constructor(private element: ElementRef, private AnnotationsService: AppAnnotationsService) {
    }

    delete () {
        if (!this.can_delete) return;
        this.AnnotationsService.delete_tag(this.annotation);
    }

    ngOnInit () {

        let classe = 'badge-termtag';

        if (this.annotation.group === 'location') {
            classe = 'badge-geotag'
        }

        if (this.annotation.creator_type !== 'user') {
            classe += '--auto';
        }

        this.element.nativeElement.querySelector('span').classList.add(classe);

    }
}