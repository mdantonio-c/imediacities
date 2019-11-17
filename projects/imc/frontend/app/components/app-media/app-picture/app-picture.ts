import {Component, Input, OnInit, AfterViewInit, ViewChild, ElementRef} from '@angular/core';
import { AuthService } from '@rapydo/services/auth';

@Component({
    selector: 'app-picture',
    templateUrl: 'app-picture.html'
})

export class AppPictureComponent implements OnInit, AfterViewInit {

    @Input() data;
    @ViewChild('picture', { static: false }) picture: ElementRef;
    @ViewChild('maschera', { static: false }) maschera: ElementRef;
    @ViewChild('mouse_track', { static: false }) mouse_track: ElementRef;

    private rect = {
        origin: null,
        end: null,
        props : new Map()
    };

    private _drawing: boolean = false;
    private _picture;
    private _track;
    private _maschera;

    constructor(private auth: AuthService) {
    }

    mousedown (evento) {
        this.rect.origin = this.getMousePos(evento);
        this._drawing = true;
        this._maschera.setAttribute('visibility', 'hidden');
    }

    mousemove (evento) {
        if (this._drawing) {
            const pos = this.getMousePos(evento);

            const width = (pos.x - this.rect.origin.x);
            const height = (pos.y - this.rect.origin.y);

            const offsetX = (width < 0) ? width : 0;
            const offsetY = (height < 0) ? height : 0;

            this.rect.props.set('x', this.to_perc(this.rect.origin.x + offsetX, 'width'));
            this.rect.props.set('y', this.to_perc(this.rect.origin.y + offsetY, 'height'));
            this.rect.props.set('width', this.to_perc(width, 'width'));
            this.rect.props.set('height', this.to_perc(height, 'height'));
            this.rect.props.set('visibility', 'visibile');

            this.draw (this._track, this.rect.props)
        }
    }

    mouseup (evento) {
        const pos = this.getMousePos(evento);
        this._drawing = false;
        this._track.setAttribute('visibility', 'hidden');
        this.draw(this._maschera, this.rect.props);
    }

    to_perc (val, prop) {
        return Math.abs(val) * 100 / this._picture[prop] + '%';
    }

    draw (element, props) {
        props.forEach((value, key) => {
            element.setAttribute(key, value)
        })
    }

    disableSaveAs() { return false; }

    getMousePos(evento) {
        const rect = this._picture.getBoundingClientRect();
        return {
            x: evento.clientX - rect.left,
            y: evento.clientY - rect.top
        };
    }

    _picture_source_add(source_url) {
        let token = this.auth.getToken();
        this._picture.src = source_url + '&access_token=' + token;
    }

    ngOnInit() {
    }

    ngAfterViewInit () {
        this._picture = this.picture.nativeElement;

        this._picture_source_add(this.data.links.content);
        /*this._track = this.mouse_track.nativeElement;
        this._maschera = this.maschera.nativeElement;*/
    }
}