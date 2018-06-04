import {Component, Input, ViewChild, OnInit, OnChanges} from '@angular/core';
import {AppMediaService} from "../../../services/app-media";
import {GeoCoder, NguiMapComponent} from '@ngui/map';
import {AppAnnotationsService} from "../../../services/app-annotations";
import {AppShotsService} from "../../../services/app-shots";
import {AuthService} from "/rapydo/src/app/services/auth";
import {AppVideoService} from "../../../services/app-video";

@Component({
    selector: 'app-media-map',
    templateUrl: 'app-media-map.html'
})

export class AppMediaMapComponent implements OnInit, OnChanges {

    @Input() current_shot_from_video = false;
    @Input() markers;
    @Input() shots;
    @Input() draggable_markers;
    @Input() clickable_markers;

    @ViewChild(NguiMapComponent) ngMap: NguiMapComponent;

    public center = {
        lat: 0,
        lng: 0
    };

    private _current_user = null;

    public _markers = [];
    /**
     * Istanza della mappa
     * Viene assegnato dall'evento ready della mappa
     */
    public map;
    public map_styles = [
        {
            featureType: "poi.business",
            stylers: [
                { visibility: "off" }
            ]
        },{
            featureType: "poi.attraction",
            stylers: [
                { visibility: "off" }
            ]
        }
    ];
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

    public popover;

    constructor(
        private AuthService: AuthService,
        private AnnotationsService: AppAnnotationsService,
        private ShotsService: AppShotsService,
        private geoCoder: GeoCoder,
        private MediaService: AppMediaService,
        private VideoService: AppVideoService
        ) {}

    public marker_edit: any = {
        marker: null,
        address: null,
        location: {
            lat: null,
            lng: null
        },
        id: null,
        position: null,
        iri: null,
        description: null,
        iw: null,
        state: null
    };

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
     * Aggiunge un marker sul click
     * @param event
     */
    marker_add (event) {
        if (event instanceof MouseEvent) return;

        //  Verifico shot corrente
        const shots_idx = this.shots_get();

        if (!shots_idx.length) {
            return alert('No shot selected');
        }

        this.geoCoder.geocode({
            location: event.latLng
        }).subscribe(
            result => {

                if (result && result.length) {

                    this.marker_new_set(event, result[0], shots_idx);

                }
            },
            null
        )

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
            },[]),
            marker: event.target,
            owner: this._current_user.uuid === pos.creator
        };

        event.target.nguiMapComponent.openInfoWindow('iw', event.target);
    }

    /**
     * Elimina l'annotazione collegata al marker
     * @param marker
     */
    marker_delete (marker) {
        this.AnnotationsService.delete_tag(marker);
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
     * Chiude l'infowindow per la modifica / creazione del marker
     */
    marker_edit_close (remove_marker_from_map = true) {
        this.marker_edit.iw.close();
        this.marker_edit_closeclick()
    }

    /**
     * Output emesso dal pulsante di chiusura standard della infoview
     * Controllo se il marker è stato salvato diversamente lo rimuovo dalla mappa
     */
    marker_edit_closeclick() {

        if (this.marker_edit.state !== 'saved' && this.marker_edit.state !== 'updating') {
            this.marker_edit.marker.setMap(null);
        }
    }
    /**
     * Salvataggio marker
     * todo impostare shot correttamente
     */
    marker_edit_save () {

        if(this.marker_edit.state === 'updating') {
            this.AnnotationsService.delete_tag({
                id: this.marker_edit.id,
                iri: this.marker_edit.iri,
                name: this.marker_edit.address
            })
        }

        //  Impostazione shot
        let shots_idx = [];

        if (this.marker_edit.shots_idx) {
            shots_idx = this.marker_edit.shots_idx;
        }

        // if (this.current_shot_from_video) {
        //     let current_shot = this.VideoService.shot_current();
        //     console.log("current_shot",  current_shot);
        //     shots_idx = this.shots.filter(s => s.attributes.shot_num === current_shot).map(s => s.attributes.shot_num);
        // } else {
        //     shots_idx = this.shots.map(s => s.attributes.shot_num)
        // }

        if (!shots_idx.length) {
            return alert('No shot selected');
        }

        //  Ripristinare
        this.AnnotationsService.create_tag(
            //[this.shots[0].id],
            shots_idx.map(s => s.id),
            [{
                iri: this.marker_edit.iri,
                name: this.marker_edit.description || this.marker_edit.name,
                lat: this.marker_edit.location.lat,
                lng: this.marker_edit.location.lng,
            }],
            (r) => {
                this.marker_edit.state = 'saved';
                this.marker_edit.icon = null;
                this.marker_edit_close(false);
                this.ShotsService.get();
            }
        )

    }

    marker_new_set (event, result, shots_idx) {

        //  Verifico se esiste un marker precedente
        //  ed eventualmente lo rimuovo
        if (this.marker_edit.marker && this.marker_edit.state !== 'saved') {
            this.marker_edit.marker.setMap(null);
        }

        let m = new google.maps.Marker({
            position:{
                lat: event.latLng.lat(),
                lng: event.latLng.lng()
            },
            icon: 'http://maps.google.com/mapfiles/ms/icons/green-dot.png',
            map: this.map
        });

        this._markers.push(m);

        this.marker_edit = {
            marker: m,
            address: result.formatted_address,
            description: result.formatted_address,
            iri: result.place_id,
            location: {
                lat: event.latLng.lat(),
                lng: event.latLng.lng()
            },
            shots_idx: shots_idx,
            state: 'saving',
        };

        this.marker_edit.iw = this.ngMap.infoWindows.edit;
        this.ngMap.openInfoWindow('edit', m)


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
     * Aggiunge un marker dall'esterno
     * @param marker
     */
    marker_push (marker) {
        this._markers.push(marker);
    }
    /**
     * Prepara un marker esistente per la modifica e visualizza la infowindow corrispondente
     * @param annotation
     * @param marker
     */
    marker_update (annotation, marker) {
        //todo shots_idx??
        console.log("marker",  marker);
        this.marker_edit = {
            marker: marker,
            address: annotation.name,
            description: annotation.name,
            iri: annotation.iri,
            id: annotation.id,
            location: {
                lat: annotation.spatial[0],
                lng: annotation.spatial[1]
            },
            state: 'updating',
            iw: this.ngMap.infoWindows.edit
        };

        this.ngMap.infoWindows.iw.close();
        this.ngMap.infoWindows.edit.open(marker)

    }

    /**
     * Ottiene gli indici degli shot ai quali associare il marker da salvare
     * @returns {any[]}
     */
    shots_get () {
        let shots_idx = [];
        if (this.current_shot_from_video) {
            let current_shot = this.VideoService.shot_current();
            shots_idx = this.shots.filter(s => s.attributes.shot_num === current_shot)
        } else {
            shots_idx = this.shots
        }
        shots_idx = shots_idx.map(s => {
            return {
                indice: s.attributes.shot_num,
                id: s.id
            }
        });
        return shots_idx;
    }
    /**
     * Imposta la mappa in modo da visualizzare tutti i marker
     */
    fit_bounds () {

        if (this.map) {

            if (this._markers.length) {
                let bounds = new google.maps.LatLngBounds();
                this._markers.forEach(l => bounds.extend({lat: l.spatial[0], lng: l.spatial[1]}));
                this.map.fitBounds(bounds);
                this.map.panToBounds(bounds);
            } else {
                this.map.panTo(this.center);
                this.map.setZoom(14);
            }

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


    ngOnInit() {

        this._current_user = this.AuthService.getUser();

        //  Centro la mappa sul default
        let owner = this.MediaService.owner();
        if (owner.location) {
            this.center = owner.location;
        }
        this.popover = this.AnnotationsService.popover();
        this.ShotsService.update.subscribe(shots => {this.shots = shots;})
    }

    ngOnChanges () {
        //  Elimino tutti i marker eventualmente residui
        this._markers.forEach(m => {
            if (m.hasOwnProperty('map')) {
                m.setMap(null)
            }
        });

        //  Reimposto i marker
        this._markers = this.markers.slice();

        this.fit_bounds();

    }
}