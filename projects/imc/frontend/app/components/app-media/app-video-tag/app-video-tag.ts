import {Component, Input, ViewChild, ElementRef, Output, EventEmitter, AfterViewInit} from '@angular/core';
import {AppVideoControlComponent} from "../app-video-controls/app-video-control";
import {AppShotsService} from "../../../services/app-shots";

@Component({
    selector: 'app-video-tag',
    templateUrl: 'app-video-tag.html'
})

export class AppVideoTagComponent extends AppVideoControlComponent implements AfterViewInit{

    @Input() data;
    @ViewChild('termtag_slider') termtag_slider: ElementRef;
    @ViewChild('geotag_slider') geotag_slider: ElementRef;
    @Output() scena_visualizza: EventEmitter<any> = new EventEmitter();
    @Output() modale_richiedi: EventEmitter<any> = new EventEmitter();

    public min_detected = null;
    public min_width = 30;

    public termtags = null;
    public geotags = null;

    constructor() {
        super()
    }

    geotag_add () {
        this.tag_add('insert-geotag');
    }

    scene_click (idx) {
        this.scena_visualizza.emit(this.data[idx].attributes.start_frame_idx / this.parent.fps );
    }


    scene_update () {
    }

    tag_add (modale) {

        if (this.parent.shot_current < 0) {
            alert('no shot selected');
            return
        }

        this.modale_richiedi.emit({
            modale: modale,
            titolo: 'Add Tag',
            data: {shots: [this.data[this.parent.shot_current]]}
        });
    }

    termtag_add () {
        this.tag_add('insert-tag');
    }

    ngOnInit() {

        super.ngOnInit();
        this.data.forEach( s => {

            if (!this.min_detected || s.attributes.duration < this.min_detected) {
                this.min_detected = s.attributes.duration
            }

        });

    }

    ngAfterViewInit () {

        this.termtags = this.termtag_slider.nativeElement.children;
        this.geotags = this.geotag_slider.nativeElement.children;

    }

    ontimeupdate () {
        this.scene_update();
    }

}