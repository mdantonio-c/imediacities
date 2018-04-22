import {Component, Input, ViewChild, ViewChildren, OnInit, AfterViewInit ,ElementRef, ChangeDetectorRef } from '@angular/core';
import {AppVideoControlProgressBarComponent} from "../app-video-controls/app-video-control-progress-bar/app-video-control-progress-bar";
import {AppVideoControlComponent} from "../app-video-controls/app-video-control";

@Component({
    selector: 'app-video-player',
    templateUrl: 'app-video-player.html'
})

export class AppVideoPlayerComponent implements OnInit, AfterViewInit {

    @Input() data: any;
    @Input() shots: any;
    @Input() layout: any;
    @ViewChild('videoPlayer') videoPlayer: ElementRef;
    //@ViewChildren('AppVideoControlComponent') componenti;
    componenti = new Array();

    fps = 0;
    frame_lentgh = 0;

    showComponents = false;
    video;
    
    constructor(private cdRef: ChangeDetectorRef, private elRef: ElementRef ) {
    }
    
    _frame_set (f) {
        //  sporchissimo :)
        this.fps = eval(f);
        this.frame_lentgh = 1/this.fps;
    }
    
    _video_source_add (source_url) {
        let source = document.createElement('source');
        source.src = source_url;
        this.videoPlayer.nativeElement.appendChild(source);
        this.video.load();
    }

    _video_events () {

        this.video.onended = (e) => {
            this._emetti('onended', e);
        };

        this.video.onfullscreen = (e) => {
            this._emetti('onfullscreen', e);
        };

        this.video.onloadeddata = (e) => {
            this._emetti('onloadeddata', e);
        };

        this.video.onloadedmetadata = (e) => {
            this.showComponents = true;
            this._emetti('onloadedmetadata', e);
        };

        this.video.onloadstart = (e) => {
            this._emetti('onloadstart', e);
        };

        this.video.onpause = (e) => {
            this._emetti('onpause', e);
        };

        this.video.onplay = (e) => {
            this._emetti('onplay', e);
        };

        this.video.onplaying = (e) => {
            this._emetti('onplaying', e);
        };

        this.video.onprogress = (e) => {
            this._emetti('onprogress', e);
        };

        this.video.onseeked = (e) => {
            this._emetti('onseeked', e);
        };

        this.video.ontimeupdate = (e) => {
            this._emetti('ontimeupdate', e);

            if(this.video.currentTime == 0){
                this._emetti('onbegin', e);
            }

        };

        this.video.onvolumechange = (e) => {
            this._emetti('onvolumechange', e);
        };

        this.video.onwaiting = (e) => {
            this._emetti('onwaiting', e);
        };
    }

    _emetti (evento, dati) {
        this.componenti.forEach( c => {c[evento](dati)});
    }

    public jump_to (evento) {
        this.video.currentTime = evento;
    }

    public registra (evento) {
        this.componenti.push(evento);
    }

    public fullscreen (stato) {
        this.elRef.nativeElement.children[0].classList[stato === 'on' ? 'add' : 'remove']('video_container--fullscreen');
    }

    ngOnInit () {
        this._frame_set(this.data.relationships.item[0].attributes.framerate);
    }

    ngAfterViewInit () {

        if (this.layout) {
            this.elRef.nativeElement.children[0].classList.add(`video_container--${this.layout}`);
        }

        this.video = this.videoPlayer.nativeElement;
        this._video_source_add(this.data.links.content);
        this._video_events();
        this.cdRef.detectChanges();
    }
}