import {Component, OnInit, Input, ViewChild, ElementRef, AfterViewInit} from '@angular/core';

@Component({
    selector: 'app-media-tags',
    templateUrl: 'app-media-tags.html'
})

export class AppMediaTagsComponent implements OnInit, AfterViewInit{

    @ViewChild('annotation_filter') annotation_filter: ElementRef;
    @Input() shots = null;

    public annotations = null;
    public annotations_visualizzate = [];
    constructor() {
    }

    ngOnInit() {
        this.annotations = new Map();
        //  Inserisco tutti i tags in una mappa
        this.shots.forEach(s=>{

            s.annotations.tags.forEach( t => this._annotations_add(t));

            s.annotations.locations.forEach(l => this._annotations_add(l));

        });
        this.annotations = Array.from(this.annotations);
        this.annotations.sort((a,b) => {
            if (a[1].name.toLowerCase() < b[1].name.toLowerCase()) return -1;
            if (a[1].name.toLowerCase() > b[1].name.toLowerCase()) return 1;
            return 0;
        });
        this.annotations_visualizzate = this.annotations;
    }

    ngAfterViewInit () {
        this.annotation_filter.nativeElement.addEventListener('keyup', (e) => {
            this._annotations_filter(e.target.value);
        })
    }

    _annotations_add (a) {
        this.annotations.set(a.name, a);
    }

    _annotations_filter (filtro) {
        filtro = new RegExp( filtro, 'gi' );
        this.annotations_visualizzate = this.annotations.filter(a=> filtro.test(a[1].name));
    }

}