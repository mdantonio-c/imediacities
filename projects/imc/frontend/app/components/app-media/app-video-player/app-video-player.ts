import {Component, Input, ViewChild, ViewChildren, OnInit, AfterViewInit, Output, ElementRef, EventEmitter, ChangeDetectorRef } from '@angular/core';
// import {AppVideoControlProgressBarComponent} from "../app-video-controls/app-video-control-progress-bar/app-video-control-progress-bar";
// import {AppVideoControlComponent} from "../app-video-controls/app-video-control";
import {rangePlayer} from "../../../decorators/app-range";



@Component({
    selector: 'app-video-player',
    templateUrl: 'app-video-player.html'
})


export class AppVideoPlayerComponent implements OnInit, AfterViewInit {

    @Input() data: any;
    @Input() shots: any;
    @Input() layout: any;

    @ViewChild('videoPlayer') videoPlayer: ElementRef;

    advanced_show = false;

    componenti = new Array();

    fps = 0;
    frame_length = 0;

    showComponents = false;
    video = null;

    metadata = null;
    player = null;

    spinner_prevent = false;
    shot_current = -1;

    /**
     * Memorizza il punto da cui ripartire nel caso di un range in loop
     * @type {number}
     */
    restart_time = null;

    constructor(private cdRef: ChangeDetectorRef, private elRef: ElementRef ) {}

    @rangePlayer() range;

    _frame_set (f) {
        //  sporchissimo :)
        this.fps = eval(f);
        this.frame_length = 1/this.fps;
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

            this.metadata = {
                begin: 0,
                duration: this.video.duration
            };

            if (this.player === null) {
                this.player = {
                    begin: 0,
                    duration: this.video.duration
                };
            }
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
            this.spinner_prevent = false;
            this._emetti('onplay', e);
        };

        this.video.onplaying = (e) => {
            this._emetti('onplaying', e);
        };

        this.video.onprogress = (e) => {
            this._emetti('onprogress', e);
            //  todo componentizzare
            this.elRef.nativeElement.querySelector('.video_mask').classList.remove('video_mask--active');
        };

        this.video.onseeked = (e) => {
            this._emetti('onseeked', e);
            if (this.spinner_prevent) return;
            //  todo componentizzare
            this.elRef.nativeElement.querySelector('.video_mask').classList.remove('video_mask--active');
        };

        this.video.onseeking = (e) => {
            this._emetti('onseeking', e);
            if (this.spinner_prevent) return;
            //  todo componentizzare
            this.elRef.nativeElement.querySelector('.video_mask').classList.add('video_mask--active');
        };

        this.video.ontimeupdate = (e) => {
            this._emetti('ontimeupdate', e);

            // if(this.video.currentTime == 0){

            if (this.player) {

                //  Evento onbegin
                //  inizio del filmato o del range
                if (this.video.currentTime <= this.player.begin) {
                    this._emetti('onbegin', e);
                }

                //  Evento onended
                //  fine del filmato o del range
                if (this.video.currentTime >= this.player.begin + this.player.duration) {
                    this._emetti('onended', e);
                }

                //  Rilevamento shots
                let current_frame = Math.ceil(this.fps * this.video.currentTime);
                let shot_corrente = 0;
                this.shots.forEach((s,idx) => {
                    if (current_frame >= s.attributes.start_frame_idx && current_frame < s.attributes.end_frame_idx) {
                        s.attivo = true;
                        shot_corrente = idx;
                    } else {
                        s.attivo = false;
                    }
                });

                if (this.shot_current !== shot_corrente) {
                    this.shot_current = shot_corrente;
                    this._emetti('onshot_start', this.shots[shot_corrente]);
                }

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

    _play_interval (intervallo) {

    }

    public jump_to (time_or_frames, um_is_frame = false, pause = false) {

        if (pause) {
            this.video.pause();
        }

        if (um_is_frame) {
            time_or_frames =  this.frame_to_time(time_or_frames);
        }

        this.video.currentTime = time_or_frames;
    }

    public shot_play (shot_number) {
        this.jump_to(1/ this.fps * this.shots[shot_number].attributes.start_frame_idx);
    }

    public segement_play (segment) {

    }

    public registra (componente) {
        this.componenti.push(componente);
    }

    public fullscreen (stato) {
        this.elRef.nativeElement.children[0].querySelector('.video_container').classList[stato === 'on' ? 'add' : 'remove']('video_container--fullscreen');
    }

    public remove () {
        this.video.remove();
    }

    frame_to_time (frame) {
        return frame * this.frame_length;
    }

    time_to_frame (time) {
        return Math.ceil(time / this.frame_length);
    }

    frame_current () {
        return this.time_to_frame(this.video.currentTime);
    }

    _floor (number, decimal_places) {
        return Math.floor(parseFloat(number) * Math.pow(10, decimal_places)) / Math.pow(10, decimal_places);
    }

    _round (number, decimal_places) {
        return Math.round(parseFloat(number) * Math.pow(10, decimal_places)) / Math.pow(10,decimal_places);
    }

    _round_fixed (number, decimal_places) {
        return this._round(number, decimal_places).toFixed(decimal_places);
    }

    _ceil (number, decimal_places) {
        return Math.ceil(parseFloat(number) * Math.pow(10,decimal_places)) / Math.pow(10, decimal_places);
    }

    public layout_check (layout) {
        return this.shots && this.shots.length && this.layout !== layout
    }

    public advanced_control_show (stato) {
        this.advanced_show = stato;
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