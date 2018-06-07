import {Component, Input, OnInit} from '@angular/core';

@Component({
    selector: 'app-picture',
    templateUrl: 'app-picture.html'
})

export class AppPictureComponent implements OnInit {

    @Input() data;

    private rect = {
        origin: null,
        end: null
    };

    constructor() {
    }

    draw (event) {
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
}