import {Component, OnInit, ViewChild, ElementRef, AfterViewInit} from '@angular/core';
import {AppVideoControlComponent} from "../app-video-control";

@Component({
    selector: 'app-video-control-volume',
    templateUrl: 'app-video-control-volume.html'
})

export class AppVideoControlVolumeComponent extends AppVideoControlComponent implements AfterViewInit{

    @ViewChild('ico_off', { static: false }) ico_off: ElementRef;
    @ViewChild('ico_mute', { static: false }) ico_mute: ElementRef;
    @ViewChild('ico_down', { static: false }) ico_down: ElementRef;
    @ViewChild('ico_up', { static: false }) ico_up: ElementRef;
    @ViewChild('volume', { static: false }) volume: ElementRef;
    @ViewChild('volume_slider', { static: false }) volume_slider: ElementRef;
    @ViewChild('volume_gutter', { static: false }) volume_gutter: ElementRef;

    private volume_level = 'off';
    private volume_last_value = 0;

    private volume_slider_timer = 500;
    private volume_slider_timeout =null;

    constructor() {
        super();
        // this._interfaccia();
    }

    ngOnInit () {
        super.ngOnInit();
    }
    ngAfterViewInit () {
        this.volume_last_value = this.video.volume;
        this._interfaccia();
    }

    private _interfaccia () {

        if (this.video.volume < .1) {
            this.volume_level = 'off'
        } else if (this.video.volume < .4) {
            this.volume_level = 'mute';
        } else if (this.video.volume < .7) {
            this.volume_level = 'down';
        } else {
            this.volume_level = 'up';
        }

        this._volume_gutter_set(eval('this.ico_'+this.volume_level));

    }

    private _ico_events () {

        let icons = [this.ico_off, this.ico_mute, this.ico_down, this.ico_up];

        icons.forEach(i => {
            i.nativeElement.addEventListener('click', () => {
                if (i.nativeElement.id === 'ico_off') {
                    this.volume_unmute();
                } else {
                    this.volume_mute();
                }
            });
            i.nativeElement.addEventListener('mouseover', () => {
                this._volume_slider_show(i);
            });
        });

    }

    private _volume_events () {

        this.volume.nativeElement.addEventListener('click', () => {
            this.volume_set(this.volume.nativeElement.value);
        });

        this.volume.nativeElement.addEventListener('onchange', () => {
            this.volume_set(this.volume.nativeElement.value);
        });

        this.volume.nativeElement.addEventListener('mouseout', () => {
            setTimeout(() => {
                this.volume_set(this.volume.nativeElement.value);
            }, 0)


        })

    }

    private _volume_gutter_set (ico) {
        let copia = ico.nativeElement.cloneNode(true);
        copia.classList.remove('display-none');
        this.volume_gutter.nativeElement.innerHTML = "";
        this.volume_gutter.nativeElement.appendChild(copia);
    }

    private _volume_slider_events () {

        this.volume_slider.nativeElement.addEventListener('mouseleave', () => {
            this.volume_slider_timeout = setTimeout(() => {
                this.volume_slider.nativeElement.classList.remove('show')
            }, this.volume_slider_timer)
        });

        this.volume_slider.nativeElement.addEventListener('mouseenter', () => {
            clearTimeout(this.volume_slider_timeout);
            this.volume_slider_timeout = null;
        })

    }

    private _volume_slider_show (ico) {

        let elemRect = ico.nativeElement.getBoundingClientRect();

        this._volume_gutter_set(ico);

        //this.volume_slider.nativeElement.style = `top:${elemRect.top + elemRect.height}px;left:${elemRect.left}px;`;
        this.volume_slider.nativeElement.style = `top:38px;left:3px;position:absolute;`;
        this.volume_slider.nativeElement.classList.add('show');

        if (this.volume_slider_timeout === null) {
            this.volume_slider_timeout = setTimeout(() => {
                this.volume_slider.nativeElement.classList.remove('show');
                this.volume_slider_timeout = null;
            }, this.volume_slider_timer * 2)
        }

    }

    public volume_set (v, add = false) {

        let volume_new = v;
        if (add) {
            volume_new += this.video.volume;
        }

        if (volume_new > 1 || volume_new < 0) return;
        this.video.volume = volume_new;


    }

    public volume_mute () {
        this.volume_last_value = this.video.volume;
        this.volume_set(0);
    }

    public volume_unmute () {
        this.volume_set(this.volume_last_value);
    }

    ngAfterViewInit () {

        this._ico_events();
        this.volume_set(this.video.volume);
        this._volume_events();
        this.volume.nativeElement.value = this.video.volume;
        this._volume_slider_events();
        this._interfaccia();

    }

    onvolumechange () {
        this._interfaccia();
    }

}