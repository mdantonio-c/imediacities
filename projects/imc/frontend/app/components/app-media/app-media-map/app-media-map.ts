import {
  Component,
  Input,
  ViewChild,
  OnInit,
  OnChanges,
  OnDestroy,
} from "@angular/core";
import { AppMediaService } from "../../../services/app-media";

import { NominatimService } from "../../../catalog/services/nominatim.service";

import { AppAnnotationsService } from "../../../services/app-annotations";
import { AppShotsService } from "../../../services/app-shots";
import { AuthService } from "@rapydo/services/auth";
import { AppVideoService } from "../../../services/app-video";
import { AuthzService, Permission } from "../../../services/authz.service";
import { ApiService } from "@rapydo/services/api";
import { ProviderToCityPipe } from "../../../pipes/ProviderToCity";
import { is_annotation_owner } from "../../../decorators/app-annotation-owner";

import * as L from "leaflet";

import { NgbModal } from "@ng-bootstrap/ng-bootstrap";

import { CatalogService } from "../../../catalog/services/catalog.service";
import { AppMediaMapInfowindowComponent } from "../app-media-map-infowindow/app-media-map-infowindow";

@Component({
  selector: "app-media-map",
  templateUrl: "app-media-map.html",
  styleUrls: ["./app-media-map.css"],
  providers: [AuthzService],
})
export class AppMediaMapComponent implements OnInit, OnChanges, OnDestroy {
  @Input() current_shot_from_video = false;
  @Input() markers;
  @Input() shots;
  @Input() draggable_markers;
  @Input() clickable_markers;
  @Input() media_type;

  //@ViewChild(NguiMapComponent, { static: false }) ngMap: NguiMapComponent;

  @is_annotation_owner() is_annotation_owner;

  constructor(
    private api: ApiService,
    private AuthService: AuthService,
    private AuthzService: AuthzService,
    private AnnotationsService: AppAnnotationsService,
    private ShotsService: AppShotsService,
    private nominatimOsmGeocoder: NominatimService,
    private ProviderToCity: ProviderToCityPipe,
    private MediaService: AppMediaService,
    private VideoService: AppVideoService,
    private catalogService: CatalogService,
    private modalService: NgbModal
    // private mapApiLoader: CustomNgMapApiLoader
  ) {
    //mapApiLoader.setUrl();
  }

  private _subscription;

  public center = {
    lat: 0,
    lng: 0,
  };

  private _current_user = null;

  public _markers = [];

  /**
   * Stili della mappa
   * @type {{featureType: string; stylers: {visibility: string}[]}[]}
   */
  // base layer
  streetMaps = L.tileLayer(
    "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
    {
      detectRetina: true,
      attribution:
        '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    }
  );
  // Marker cluster stuff
  markerClusterGroup: L.MarkerClusterGroup;
  markerClusterData: L.Marker[] = [];
  markerClusterOptions: L.MarkerClusterGroupOptions;
  osmap: L.Map;
  lastMouseLat: any;
  lastMouseLng: any;



  // Set the initial set of displayed layers
  options = {
    layers: [this.streetMaps],
    zoom: 4,
    center: [0 ,0],
  };






  public map_styles = [
    {
      featureType: "poi.business",
      stylers: [{ visibility: "off" }],
    },
    {
      featureType: "poi.attraction",
      stylers: [{ visibility: "off" }],
    },
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
      updated: null,
    },
  };

  public popover;

  public marker_edit: any = {
    marker: null,
    address: null,
    location: {
      lat: null,
      lng: null,
    },
    id: null,
    position: null,
    iri: null,
    description: null,
    iw: null,
    state: null,
  };

  /**
   * Imposta il marker attivo quando ne viene iniziato il trascinamento
   * @param target
   * @param updated_position
   * @param location
   * @param original_position
   */
  marker_active_set(target, updated_position, location, original_position) {
    this.marker_active = {
      marker: target,
      location: location,
      position: {
        original: original_position,
        updated: updated_position,
      },
    };
  }

  /**
   * Rimuove il riferimento al marker attivo
   */
  marker_active_unset() {
    this.marker_active = {
      marker: null,
      location: null,
      position: {
        original: null,
        updated: null,
      },
    };
  }

  /**
   * Aggiunge un marker sul click
   * @param event
   */
  marker_add(event) {

    // why??????
    // if (event instanceof MouseEvent) return;

    if (
      !this.AuthzService.hasPermission(
        this._current_user,
        this.MediaService.media(),
        Permission.CREATE_ANNOTATION
      )
    )
      return;

    let shots_idx = [];

    //  Verifico shot corrente
    if (this.media_type === "video" && this.current_shot_from_video) {
      if (this.VideoService.shot_current() === -1) {
        return alert("No shot selected");
      }
      shots_idx = this._shots_get(this.VideoService.shot_current());
    } else {
      shots_idx = this._shots_get(this.shots.map((s) => s.shot_num));
    }

    if (this.media_type === "video" && !shots_idx.length) {
      return alert("No shot selected");
    }
    const geocode =  this.nominatimOsmGeocoder.reverse(this.lastMouseLat, this.lastMouseLng).subscribe(result => {
      if (result && result.display_name) {
        this.marker_new_set(event, result, shots_idx);
      }
    });
    this._subscription.add(geocode);
  }


  /**
   * Visulizza la InfoWindow al click su un marker
   * @param event
   * @param pos
   */
  marker_click(event, pos) {
    if (!this.clickable_markers) {
      return;
    }
    this.info_window_data = {
      annotations: [pos],
      shots: pos.shots_idx.reduce((acc, s) => {
        if (this.shots.length > s) {
          acc.push(this.shots[s]);
        }
        return acc;
      }, []),
      marker: event.target,
      owner: this.is_annotation_owner(this._current_user, pos.creator),
    };

    event.target.nguiMapComponent.openInfoWindow("iw", event.target);
  }

  /**
   * Elimina l'annotazione collegata al marker
   * @param marker
   */
  marker_delete(marker) {
    this.AnnotationsService.delete_tag(marker, this.media_type);
  }

  /**
   * Al termine del trascinamento di un marker mostra una InfoWindow con le opzioni possibili
   * @param event
   * @param pos
   */
  marker_dragend(event, pos) {
    this.marker_active_set(
      event.target,
      {
        lat: parseFloat(event.latLng.lat()),
        lng: parseFloat(event.latLng.lng()),
      },
      pos,
      { lat: parseFloat(pos.spatial[0]), lng: parseFloat(pos.spatial[1]) }
    );
    event.target.nguiMapComponent.openInfoWindow("move", event.target);
  }

  /**
   * Chiude l'infowindow per la modifica / creazione del marker
   */
  marker_edit_close(remove_marker_from_map = true) {
    this.marker_edit.iw.close();
    this.marker_edit_closeclick();
  }

  /**
   * Output emesso dal pulsante di chiusura standard della infoview
   * Controllo se il marker è stato salvato diversamente lo rimuovo dalla mappa
   */
  marker_edit_closeclick() {
    if (
      this.marker_edit.state !== "saved" &&
      this.marker_edit.state !== "updating"
    ) {
      this.marker_edit.marker.setMap(null);
    }
  }

  /**
   * Salvataggio marker
   */
  marker_edit_save() {
    //  Impostazione shot
    let shots_idx = [];

    if (this.marker_edit.shots_idx) {
      shots_idx = this.marker_edit.shots_idx;
    }

    if (this.media_type === "video" && !shots_idx.length) {
      return alert("No shot selected");
    }

    if (this.marker_edit.state === "updating") {
      this.AnnotationsService.delete_tag(
        {
          id: this.marker_edit.id,
          iri: this.marker_edit.iri,
          name: this.marker_edit.address,
          source_uuid: this.marker_edit.source_uuid,
        },
        this.media_type
      );
    }

    this.AnnotationsService.create_tag(
      shots_idx.map((s) => s.id),
      [
        {
          iri: this.marker_edit.iri,
          name: this.marker_edit.description || this.marker_edit.name,
          lat: this.marker_edit.location.lat,
          lng: this.marker_edit.location.lng,
        },
      ],
      this.media_type,
      (r) => {
        if (this.media_type === "video") {
          if (this.marker_edit.state !== "updating") {
            this.ShotsService.get();
          }
        } else if (this.media_type === "image") {
          this.AnnotationsService.get(this.MediaService.media_id(), "images");
        }

        this.marker_edit.state = "saved";
        this.marker_edit.icon = null;

        this.marker_edit_close(false);
      }
    );
  }
  
  
  


  marker_new_set(event, result, shots_idx) {

    let greenIcon = L.icon({
      iconUrl: '/app/custom/assets/images/marker-icon-green.png',
      // shadowUrl: 'leaf-shadow.png',

      iconSize:     [25, 41], // size of the icon
      //shadowSize:   [x, x], // size of the shadow
      iconAnchor:   [12, 40], // point of the icon which will correspond to marker's location
      // shadowAnchor: [4, 62],  // the same for the shadow
      popupAnchor:  [-3, -76] // point from which the popup should open relative to the iconAnchor
    });

    //  Verifico se esiste un marker precedente
    //  ed eventualmente lo rimuovo
    if (this.marker_edit.marker && this.marker_edit.state !== "saved") {
      this.marker_edit.marker.setMap(null);
    }

    let m = L.marker([this.lastMouseLat, this.lastMouseLng], {icon: greenIcon}).addTo(this.osmap);
    this.marker_edit = {
      marker: m,
      address: result.display_name,
      description: result.display_name,
      iri: result.place_id,
      location: {
        lat: event.latLng.lat(),
        lng: event.latLng.lng(),
      },
      shots_idx: shots_idx,
      state: "saving",
    };

    let props = {
      marker_edit : {
        description : "aaaaaaaaaaaaaaaaaa",
        address : "bbbbbbbbbbbb"
      }
    };

    console.log('openInfoWindow', props);
    const modalRef = this.modalService.open(AppMediaMapInfowindowComponent, {
      size: "l",
      centered: true,
    });
    modalRef.componentInstance.properties = props;

    /*
    // mi serve il place name di google da salvare dentro description
    //  dentro result non c'è, faccio una richiesta a google
    const placeDetails = new google.maps.places.PlacesService(
      this.map
    ).getDetails(
      {
        placeId: result.place_id,
      },
      (placeResult, status) => {
        //console.log("marker_new_set: placeResult="+JSON.stringify(placeResult));
        //console.log("marker_new_set: status="+JSON.stringify(status));
        if (status === google.maps.places.PlacesServiceStatus.OK) {
          if (placeResult) {
            //this.marker_new_set2(event, shots_idx, placeResult, m);
            //console.log("marker_new_set: placeResult.name="+JSON.stringify(placeResult.name));
            this.marker_edit.description = placeResult.name;
          }
        } else {
          console.log("Error in Google maps PlacesService");
        }
        this.marker_edit.iw = this.ngMap.infoWindows.edit;
        this.ngMap.openInfoWindow("edit", m);
      }
    );
    */
  }

  /**
   * Riporta il marker che è stato spostato alla posizione iniziale
   */
  marker_position_reset() {
    this.marker_active.marker.setPosition(this.marker_active.position.original);
    this.marker_active.marker.nguiMapComponent.closeInfoWindow("move");
    this.marker_active_unset();
  }

  /**
   * Aggiorna la posizione del marker attribuendo un nuovo titolo ottenuto dal servizio di geocoding
   */
  marker_position_update() {
    /* TODO TODO TODO
    new google.maps.Geocoder().geocode(
      { location: this.marker_active.position.updated },
      (results, status) => {
        //  Aggiorno proprietà marker
        let indirizzi = results[0].address_components;
        let titolo;

        indirizzi.some((i) => {
          if (i.types.indexOf("route") !== -1) {
            titolo = i.long_name;
            return true;
          }
        });

        this.marker_active.marker.setTitle(titolo);

        //  Aggiorno proprietà location
        this.marker_active.location.name = titolo;
        this.marker_active.location.spatial = [
          this.marker_active.position.updated.lat,
          this.marker_active.position.updated.lng,
        ];
        this.marker_active.location.iri = results[0].place_id;

        this.marker_active.marker.nguiMapComponent.closeInfoWindow("move");
        this.marker_active_unset();
      }
    );
    */
  }

  /**
   * Aggiunge un marker dall'esterno
   * @param marker
   */
  marker_push(marker) {
    this._markers.push(marker);
  }

  marker_remove(marker) {
    this._markers = this._markers.filter((m) => m.name != marker.name);
  }

  /**
   * Prepara un marker esistente per la modifica e visualizza la infowindow corrispondente
   * @param annotation
   * @param marker
   */
  marker_update(annotation, marker) {

/* TODO TODO TODO 

    this.marker_edit = {
      marker: marker,
      address: annotation.name,
      description: annotation.name,
      iri: annotation.iri,
      id: annotation.id,
      source_uuid: annotation.source_uuid,
      shots_idx: this._shots_get(annotation.shots_idx),
      location: {
        lat: annotation.spatial[0],
        lng: annotation.spatial[1],
      },
      state: "updating",
      iw: this.ngMap.infoWindows.edit,
    };

    this.ngMap.infoWindows.iw.close();
    this.ngMap.infoWindows.edit.open(marker);
    */
  }

  /**
   * Ottiene gli indici degli shot ai quali associare il marker da salvare
   * @returns {any[]}
   */
  _shots_get(elenco_shots = null) {
    if (!elenco_shots || !Array.isArray(elenco_shots)) {
      elenco_shots = [elenco_shots];
    }

    let shots_idx = [];

    elenco_shots.forEach((e) => {
      this.shots.forEach((s) => {
        if (s.shot_num === e) {
          shots_idx.push(s);
        }
      });
    });

    shots_idx = shots_idx.map((s) => {
      return {
        indice: s.shot_num,
        id: s.id,
      };
    });

    return shots_idx;
  }

  /**
   * Imposta la mappa in modo da visualizzare tutti i marker
   */
  fit_bounds() {

    console.log('Checkpoint fit_bounds');

    if (this.osmap) {
      if (this._markers.length) {
        var mks = [];
        this._markers.forEach((l) => {
          let m = L.marker([l.spatial[0], l.spatial[1]]).addTo(this.osmap);
          mks.push(m);
          console.log('Checkpoint marker' , l);
        });

        
        var mkGroup = L.featureGroup(mks);
        this.osmap.fitBounds(mkGroup.getBounds().pad(0.5));


        /*    TODO TODO TODO 
        let bounds = new google.maps.LatLngBounds();
        this._markers.forEach((l) =>
          bounds.extend({ lat: l.spatial[0], lng: l.spatial[1] })
        );



        this.map.fitBounds(bounds);
        this.map.panToBounds(bounds);
      } else {
        if (this.center.lat !== 0 || this.center.lng !== 0) {
          this.map.panTo(this.center);
          this.map.setZoom(14);
        } else {
          const currentCenter = this.map.getCenter();
          if (currentCenter)
            if (currentCenter.lat() !== 0 && currentCenter.lng() !== 0) return;
        }*/
      }
    }
  }

  /**
   * Evento ready della mappa
   * imposta this.map
   * @param map
   */
  onMapReady(map: L.Map) {

    console.log("Checkpoint  onMapReady ", map);

    this.osmap = map;
    var componentRef = this;
    this.osmap.addEventListener('mousemove', function(ev) {
      componentRef.lastMouseLat = ev.latlng.lat;
      componentRef.lastMouseLng = ev.latlng.lng;
   });

    this.set_center_from_owner();

    this.fit_bounds();
  }

  set_center_from_owner() {
    const _media_owner = this.MediaService.owner();

    if (_media_owner  /* && _media_owner.shortname */ ) {

      let location_to_find = _media_owner.shortname;
      if(!location_to_find) {
            /*
            //  NSI: aggiunto il codice sottostante perchè l'immagine
            //        di prova aveva "test" come owner
            let location_to_find = null;
            if (_media_owner.shortname.length === 3) {
                location_to_find = _media_owner.shortname;
            } else {
                location_to_find = 'ccb';
            }
            */
        location_to_find = 'ccb';
      }


           
      if (location_to_find) {
        this.centerCity(location_to_find.toUpperCase());
/*

        console.log('check stuff', location_to_find);

        var geocode = this.nominatimOsmGeocoder.addressLookup(location_to_find)
          .subscribe(results => {
            // look outside in order to enrich details for that given place id
            // console.log('Checkpoint Nominatim Results:', results);
            if(results.length > 0 ) {
              console.log("where the heck is center? " , results)
              this.center = {
                lat: 0, // results[0].geometry.location.lat(),
                lng: 0  //results[0].geometry.location.lng(),
              };

              this.fit_bounds();}
            
            //if (results[0]) {
            //  target.marker.properties.address = results[0].formatted_address
            //}
          },
          (error) => { console.error("GEOCODING ERROR ", error)}
        );
        this._subscription.add(geocode);
        */
      }
    }
  }

    /**
   * Center the map on a given city.
   * @param city - Archive ID (e.g. CCB)
   */
  centerCity = function (provider) {
    if (this.osmap === undefined) {
      console.warn("The center cannot be set because the map is undefined.");
      return;
    }

    let cityPosition = this.catalogService.getProviderPosition(provider);
    this.osmap.setView(new L.LatLng(cityPosition[0], cityPosition[1]), 14);
    this.center = { lat: cityPosition[0], lng: cityPosition[1] };

  };

  ngOnInit() {
    this.popover = this.AnnotationsService.popover();
    this._subscription = this.ShotsService.update.subscribe((shots) => {
      this.shots = shots;
    });
    this._current_user = this.AuthService.getUser();
  }

  ngOnChanges() {
    //  Elimino tutti i marker eventualmente residui
    this._markers.forEach((m) => {
      if (m.hasOwnProperty("map")) {
        m.setMap(null);
      }
    });
    //  Reimposto i marker
    if (this.markers && this.markers.length) {
      this._markers = this.markers.slice();
    }
    this.fit_bounds();
  }

  ngOnDestroy() {
    this._subscription.unsubscribe();
  }
}
