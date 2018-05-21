import {Component, OnInit, ViewChild} from '@angular/core';
import {AppVideoControlComponent} from "../app-video-control";
import {AppVideoControlFieldComponent} from "../app-video-control-field/app-video-control-field";

@Component({
    selector: 'app-video-control-range',
    templateUrl: 'app-video-control-range.html'
})

export class AppVideoControlRangeComponent extends AppVideoControlComponent{

    @ViewChild('from') from: AppVideoControlFieldComponent;
    @ViewChild('to') to: AppVideoControlFieldComponent;

    constructor() {
        super()
    }

    range_play () {

        if (this.parent && this.video) {
            this.parent.range.set({
                index: -1,
                start: this.from.value(),
                end: this.to.value(),
                video: this.parent
            });
            this.video.play()
        }
    }

    range_save () {
        alert('todo')
    }


}