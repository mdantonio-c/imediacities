import {Component, Input, Output, EventEmitter, OnInit} from '@angular/core';

@Component({
    selector: 'app-video-control',
    template: ''
})

export class AppVideoControlComponent implements OnInit {

    @Input() video;
    @Output() current_component: EventEmitter<any> = new EventEmitter();

    constructor() {}

    ngOnInit () {
        this.current_component.emit(this);
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
    public ontimeupdate () {};
    public onvolumechange () {}
    public onwaiting () {};

}