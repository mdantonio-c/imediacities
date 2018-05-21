import {Component, Input, OnInit, ViewChild} from '@angular/core';


@Component({
    selector: 'app-media-map',
    templateUrl: 'app-media-map.html'
})

export class AppMediaMapComponent implements OnInit {

    @Input() locations;
    @Input() shots;
    @Input() draggable_markers;
    @Input() clickable_markers;

    public center = {
        lat: 44.49488700000001,
        lng: 11.342616200000066
    };

    /**
     * Istanza della mappa
     * Viene assegnato dall'evento ready della mappa
     */
    public map;
    /**
     * Dati da passare all'InfoWindow
     * @type {{}}
     */
    public info_window_data: any = {};
    /**
     * Marker trascinato
     * @type {{marker: null; location: null; position: {original: null; updated: null}}}
     */
    public marker_active = {
        marker: null,
        location: null,
        position: {
            original: null,
            updated: null
        }
    };

    constructor() {
    }

    /**
     * Imposta il marker attivo quando ne viene iniziato il trascinamento
     * @param target
     * @param updated_position
     * @param location
     * @param original_position
     */
    marker_active_set (target, updated_position, location, original_position) {
        this.marker_active = {
            marker: target,
            location: location,
            position: {
                original: original_position,
                updated: updated_position
            }
        }
    }
    /**
     * Rimuove il riferimento al marker attivo
     */
    marker_active_unset () {
        this.marker_active = {
            marker: null,
            location: null,
            position: {
                original: null,
                updated: null
            }
        }
    }

    /**
     * Aggiunge un marker sul click // todo
     * @param event
     */
    marker_add (event) {
        //   TODO
        if (event instanceof MouseEvent) return;
        console.log("event",  event);
        console.log("this.locations",  this.locations);
    }

    /**
     * Visulizza la InfoWindow al click su un marker
     * @param event
     * @param pos
     */
    marker_click (event, pos) {

        if (!this.clickable_markers) {return}

        this.info_window_data = {
            annotations: [pos],
            shots: pos.shots_idx.reduce((acc, s) => {
                if(this.shots.length > s) {
                    acc.push(this.shots[s]);
                }
                return acc;
            },[])
        };

        event.target.nguiMapComponent.openInfoWindow('iw', event.target);
    }
    /**
     * Al termine del trascinamento di un marker mostra una InfoWindow con le opzioni possibili
     * @param event
     * @param pos
     */
    marker_dragend (event, pos) {
        this.marker_active_set(
            event.target,
            {lat: parseFloat(event.latLng.lat()), lng: parseFloat(event.latLng.lng())},
            pos,
            {lat: parseFloat(pos.spatial[0]), lng: parseFloat(pos.spatial[1])},
        );
        event.target.nguiMapComponent.openInfoWindow('move', event.target);
    }
    /**
     * Riporta il marker che è stato spostato alla posizione iniziale
     */
    marker_position_reset () {
        this.marker_active.marker.setPosition(this.marker_active.position.original);
        this.marker_active.marker.nguiMapComponent.closeInfoWindow('move');
        this.marker_active_unset();
    }
    /**
     * Aggiorna la posizione del marker attribuendo un nuovo titolo ottenuto dal servizio di geocoding
     */
    marker_position_update () {

        new google.maps.Geocoder().geocode({location:this.marker_active.position.updated}, (results, status) => {

                //  Aggiorno proprietà marker
                let indirizzi = results[0].address_components;
                let titolo;

                indirizzi.some(i => {
                    if(i.types.indexOf('route') !== -1) {
                        titolo = i.long_name;
                        return true;
                    }
                });

                this.marker_active.marker.setTitle(titolo);

                //  Aggiorno proprietà location
                this.marker_active.location.name = titolo;
                this.marker_active.location.spatial = [this.marker_active.position.updated.lat, this.marker_active.position.updated.lng];
                this.marker_active.location.iri = results[0].place_id;

                this.marker_active.marker.nguiMapComponent.closeInfoWindow('move');
                this.marker_active_unset();
            });
    }
    /**
     * Imposta la mappa in modo da visualizzare tutti i marker
     */
    fit_bounds () {
        if (this.locations.length && this.map) {
            let bounds = new google.maps.LatLngBounds();
            this.locations.forEach(l => bounds.extend({lat: l.spatial[0], lng: l.spatial[1]}));
            this.map.fitBounds(bounds);
            this.map.panToBounds(bounds);
        }
    }

    /**
     * Evento ready della mappa
     * imposta this.map
     * @param map
     */
    onMapReady (map) {
        this.map = map;
        this.fit_bounds();
    }


    ngOnInit() {}
}