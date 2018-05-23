import {Component, Input, OnInit} from '@angular/core';
import {AppVideoService} from "../../../services/app-video";

@Component({
    selector: 'app-shot-reference',
    templateUrl: 'app-shot-reference.html'
})

export class AppShotReferenceComponent implements OnInit {

    @Input() shot;

    constructor(private VideoService: AppVideoService) {
    }

    shot_play () {
        this.VideoService.shot_play(this.shot.attributes.shot_num)
    }

    ngOnInit() {
    }
}