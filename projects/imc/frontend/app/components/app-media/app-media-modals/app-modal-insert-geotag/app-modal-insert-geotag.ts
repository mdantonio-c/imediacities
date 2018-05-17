import {Component, Input, OnInit, ViewChild, ElementRef, Output, EventEmitter} from '@angular/core';
import {HttpClient, HttpHeaders} from '@angular/common/http';
import {AppAnnotationsService} from "../../../../services/app-annotations";
@Component({
    selector: 'app-modal-insert-geotag',
    templateUrl: 'app-modal-insert-geotag.html'
})

export class AppModalInsertGeotagComponent {

    @Input() data;

    @Output() shots_update: EventEmitter<any> = new EventEmitter();

    @ViewChild('search_field') search_field: ElementRef;

    ricerca_risultati;

    constructor (private AnnotationsService: AppAnnotationsService) {}

    ricerca (event) {

    }
    //AIzaSyCkSQ5V_EWELQ6UCvVGBwr3LCriTAfXypI

    save () {
        console.log("save",  this);
        this.AnnotationsService.create_tag(
            this.data.shots[0].id,
            [{
                "iri":"ChIJC8RR6ZjUf0cRQZSkWwF84aI",
                "name":"Bologna",
                "lat":44.49488700000001,
                "long":11.342616200000066
            }],
            (r) => {this.shots_update.emit(r)}
        )
    }

}