import {Component, Input, OnInit} from '@angular/core';

@Component({
    selector: 'app-video-shot',
    templateUrl: 'app-video-shot.html'
})

export class AppVideoShotComponent implements OnInit {

    @Input() data;
    @Input() multiSelection;
    

    public expansion = false;
    public checkbox_selection_label = 'multi-annotation';
    public collapse_id = 'collapse-details';

    constructor() {
    }

    expandDetailsShot(){
        this.expansion = !this.expansion;
    }

    ngOnInit() {
        this.checkbox_selection_label += this.data.attributes.shot_num;
        this.collapse_id += this.data.attributes.shot_num;
    }
}