import {Component, Input, OnInit, AfterViewInit, ViewChild, ElementRef} from '@angular/core';

@Component({
    selector: 'app-picture',
    templateUrl: 'app-picture.html'
})

export class AppPictureComponent implements OnInit, AfterViewInit {

    @Input() data;
    @ViewChild ('picture') picture: ElementRef;
    @ViewChild ('maschera') maschera: ElementRef;
    @ViewChild ('mouse_track') mouse_track: ElementRef;

    private rect = {
        origin: null,
        end: null,
        props : new Map()
    };

    private _drawing: boolean = false;
    private _picture;
    private _track;
    private _maschera;

    constructor() {
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

    getMousePos(evento) {
        const rect = this._picture.getBoundingClientRect();
        return {
            x: evento.clientX - rect.left,
            y: evento.clientY - rect.top
        };
    }

    draw_old (event) {
        // @TODO ottimizzare, inserire trascinamento ecc...
        const picture = document.querySelector('#picture').getBoundingClientRect();
        const pic = {
            width: picture.width,
            height: picture.height
        };
        console.log("pic",  pic);
        const mainSVG = document.querySelector('svg');
        const mouse = mainSVG.createSVGPoint();
        const mask = document.querySelector('#maschera');
        mouse.x = event.clientX;
        mouse.y = event.clientY;
        if (!this.rect.origin) {
            this.rect.origin = mouse.matrixTransform(mainSVG.getScreenCTM().inverse());
            mask.setAttribute('x', (this.rect.origin.x*100 / pic.width) + '%');
            mask.setAttribute('y', (this.rect.origin.y*100/pic.height)+'%');
            mask.setAttribute('width', '0');
            mask.setAttribute('height', '0');

            this.rect.end = null;

        } else {
            this.rect.end = mouse.matrixTransform(mainSVG.getScreenCTM().inverse());
            mask.setAttribute('width', ((this.rect.end.x - this.rect.origin.x)*100 / pic.width) + '%');
            mask.setAttribute('height', ((this.rect.end.y - this.rect.origin.y)*100 / pic.height) + '%');

            this.rect.origin = null;
        }
        console.log("this.rect",  this.rect);
        console.log("mask",  mask);



    }

    ngOnInit() {
    }

    ngAfterViewInit () {
        this._picture = this.picture.nativeElement;
        this._track = this.mouse_track.nativeElement;
        this._maschera = this.maschera.nativeElement;
    }
}