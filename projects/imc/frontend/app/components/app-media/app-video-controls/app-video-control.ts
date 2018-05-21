import {Component, Input, Output, EventEmitter, OnInit, OnChanges} from '@angular/core';

@Component({
    selector: 'app-video-control',
    template: ''
})

export class AppVideoControlComponent implements OnInit, OnChanges {

    @Input() parent;

    public video = null;
    @Output() current_component: EventEmitter<any> = new EventEmitter();

    constructor() {}

    ngOnInit () {
        this.current_component.emit(this);
    }

    ngOnChanges () {
        this.video = this.parent.video;
    }

    public onbegin () {}            //  evento custom: il video è a currentTime = 0
    public onended () {};
    public onfullscreen () {}       //  evento custom: il video è in fullscreen
    public onloadeddata () {};
    public onloadedmetadata () {};
    public onloadstart () {};
    public onpause () {};
    public onplay () {};
    public onplaying () {};
    public onprogress () {};
    public onseeked () {};
    public onseeking () {};
    public ontimeupdate () {};
    public onvolumechange () {}
    public onwaiting () {};

    public onrange_start (e) {};     //  evento custom
    public onrange_end (e) {};       //  evento custom

    public onshot_start (e) {};      //  evento custom

}