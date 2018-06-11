import {Component, ChangeDetectorRef, Input, OnInit, OnChanges, ViewChild, ElementRef, Output, EventEmitter} from '@angular/core';
import {HttpClient, HttpHeaders} from '@angular/common/http';
import {AppAnnotationsService} from "../../../../services/app-annotations";
import { } from '@types/googlemaps';
import {} from '@ngui';
import {AppMediaMapComponent} from "../../app-media-map/app-media-map";

@Component({
    selector: 'app-modal-insert-geotag',
    templateUrl: 'app-modal-insert-geotag.html'
})

export class AppModalInsertGeotagComponent implements  OnInit, OnChanges{

    @Input() data;
    @Input() media_type: string;
    @Output() shots_update: EventEmitter<any> = new EventEmitter();
    @ViewChild('map') mappa: AppMediaMapComponent;

    /**
     * Oggetto autocomplete per ricerca
     */
    autocomplete: any;
    address: any = {};
    center: any;
    markers = [];
    places_to_add = [];

    embargo_enable = false;
    embargo_model;

    constructor (
        private AnnotationsService: AppAnnotationsService,
        private ref: ChangeDetectorRef
        ) {}

    /**
     * Evento di inizializzazione del componente Autocomplete
     * Ritorna il riferimento a se stesso
     * @param autocomplete
     */
    initialized(autocomplete: any) {
        this.autocomplete = autocomplete;
    }
    /**
     * Aggiunge un place selezionato tramite Autocomplete
     * @param place
     */
    ricerca (place) {

        if (!place || !place.geometry) {
            return;
        }

        this.address = {};

        this.center = place.geometry.location;

        for (let i = 0; i < place.address_components.length; i++) {
            let addressType = place.address_components[i].types[0];
            this.address[addressType] = place.address_components[i].long_name;
        }

        let marker = {
            name: this.address.route || this.address.locality || this.address.country || this.address.administrative_area_level_2 || this.address.administrative_area_level_1,
            creator_type: 'user',
            group: 'location',
            place: place,
            icon: 'http://maps.google.com/mapfiles/ms/icons/green-dot.png',
            spatial: [place.geometry.location.lat(), place.geometry.location.lng()],
        };

        this.places_to_add.push(marker);
        this.mappa.marker_push(marker);
        //this.markers.push(marker);

        this.fit_bounds();
        this.ref.detectChanges();

    }
    /**
     * Rimuove un place precedente aggiunto
     * @param place
     */
    place_remove (place) {
        this.places_to_add = this.places_to_add.filter(p => p.name !== place.name);
        this.mappa.marker_remove(place);
        
        this.fit_bounds();
        this.ref.detectChanges();
    }
    /**
     * Richiama il metodo fitBounds della mappa per centrare i marker aggiunt/tolti
     */
    fit_bounds () {
        if (!this.mappa) return;
        setTimeout( () => this.mappa.fit_bounds(), 0);
    }
    /**
     * Salva un geotag come annotazione
     */
    save () {
        if (this.places_to_add.length) {
            this.AnnotationsService.create_tag(
                this.data.shots.map(s => s.id),
                this.places_to_add.map(p => {return {
                    "iri": p.place.place_id,
                    "name": p.name,
                    "lat": p.place.geometry.location.lat(),
                    "lng": p.place.geometry.location.lng()
                }}),
                this.media_type,
                (r) => {this.shots_update.emit(r)}
            )
        }

    }

    ngOnInit () {}

    ngOnChanges () {
        this.places_to_add = [];
        this.markers = this.AnnotationsService.merge(this.data.shots,'locations');
        this.fit_bounds();
    }

}