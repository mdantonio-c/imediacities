import {
  Component,
  Input,
  Output,
  ViewChild,
  ElementRef,
  Renderer2,
  EventEmitter,
  ChangeDetectorRef,
  OnInit,
  OnChanges,
} from "@angular/core";

import { CatalogService, SearchFilter } from "../../services/catalog.service";
import { NominatimService } from "../../services/nominatim.service";
// import { GeoCoder, NguiMapComponent } from "@ngui/map";

import { NotificationService } from "@rapydo/services/notification";
// import { CustomNgMapApiLoader } from "@app/services/ngmap-apiloader-service";

import { MapInfowindowComponent } from "../map-infowindow/map-infowindow.component"


import * as L from "leaflet";
import "leaflet.markercluster";

import { NgbModal } from "@ng-bootstrap/ng-bootstrap";



const europeCenter = { lat: 45, lng: 14 };
/*
const mapStyles = {
  default: null,
  hide: [
    {
      featureType: "poi.business",
      stylers: [
        {
          visibility: "off",
        },
      ],
    },
    {
      featureType: "transit",
      elementType: "labels.icon",
      stylers: [
        {
          visibility: "off",
        },
      ],
    },
  ],
};
*/
export interface MediaTag {
  annotations: any[];
  source: MediaSource;
}
export interface MediaSource {
  external_ids: string[];
  provider: string;
  rights_status: string;
  title: string;
  type: string;
  uuid: string;
  year: string;
}
declare var MarkerClusterer: any;

interface LMarkerPlus extends L.Marker {
  properties: any;
}

@Component({
  selector: "search-map",
  templateUrl: "./search-map.component.html",
  styleUrls: ["./search-map.component.css"],
})
export class SearchMapComponent implements OnInit, OnChanges {
  @Input() countByProviders: any;
  @Input() filter: SearchFilter;
  @Output() onMapChange: EventEmitter<any> = new EventEmitter<string>();

  private zoom : 4;
  private center;
  private reloading: boolean = false;
  // mapStyle = mapStyles.hide;
  radius: number = 1600 * 1000; // for zoom level 4
  markers: any[] = [];
  markerClusterer;
  showMapBoundary: boolean = false;
  counters = [];
  autocomplete: any;

  // @ViewChild(NguiMapComponent, { static: false })
  // private ngMap: NguiMapComponent;
  @ViewChild("customControl", { static: false })
  private customControl: ElementRef;
  @ViewChild("placeControl", { static: false })
  private placeControl: ElementRef;

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

  // Set the initial set of displayed layers
  options = {
    layers: [this.streetMaps],
    zoom: 4,
    center: [europeCenter.lat, europeCenter.lng],
  };



  marker: any = {};

  constructor(
    private catalogService: CatalogService,
    private nominatimOsmGeocoder: NominatimService,
    // private geoCoder: GeoCoder,
    private ref: ChangeDetectorRef,
    private notify: NotificationService,
    private renderer: Renderer2, // private mapApiLoader: CustomNgMapApiLoader
    private modalService: NgbModal
  ) {
    // mapApiLoader.setUrl();
  }

  initialized(autocomplete: any) {
    this.autocomplete = autocomplete;
  }

  placeChanged(place) {
    if (!place || !place.geometry) {
      return;
    }
    
    console.warn('check placeChanged');
    this.osmap.setView(new L.LatLng(place.geometry.location.lat, place.geometry.location.lng), 14);

    this.ref.detectChanges();
  }

  ngOnInit() {
    if (!this.filter.provider) {
      this.loadCountByProvider();
    }
  }

  ngOnChanges() {
    // update counters
    if (!this.filter.provider) {
      this.loadCountByProvider();
    }
  }

  private loadCountByProvider() {
    this.counters = [];
    if (this.countByProviders === undefined) {
      return;
    }
    for (let key of Object.keys(this.countByProviders)) {
      let city = this.catalogService.getProviderCity(key);
      if (!city) {
        console.warn(`Undefined city for provider ID ${key}`);
        continue;
      }
      let entry = {
        name: city.name,
        position: city.position,
        counter: this.countByProviders[key],
        provider: key,
      };
      this.counters.push(entry);
    }
  }

  centerEurope = function () {
    this.osmap.panTo(new L.LatLng(europeCenter.lat, europeCenter.lng));
    this.osmap.setZoom(4);
  };

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

  toggleBoundary = function () {
    this.showMapBoundary = !this.showMapBoundary;
  };

  onMapReady(map: L.Map) {
    this.osmap = map;

    let self = this;
    //
    this.osmap.on('moveend', function(e) {
      self.onCenterChanged(e);
    });
    this.osmap.on('zoomend', function(e) {
      self.onZoomChanged(e);
    });  
    //
    /*
        // add custom controls
        map.controls[google.maps.ControlPosition.TOP_RIGHT].push(
          this.customControl.nativeElement
        );
        map.controls[google.maps.ControlPosition.TOP_LEFT].push(
          this.placeControl.nativeElement
        );
        */
    //

    // this.zoom = this.osmap.getZoom();
    this.filter.provider != null
      ? this.centerCity(this.filter.provider)
      : this.centerEurope();

    this.center = {
      lat: this.osmap.getCenter().lat,
      lng: this.osmap.getCenter().lng
    }
  }

  markerClusterReady(group: L.MarkerClusterGroup) {
    this.markerClusterGroup = group;
  }

  onIdle(event) {
    console.log("map", event.target);
  }

  onZoomChanged(event) {
    if (!this.osmap) {
      return;
    }
    if (!this.reloading) {
      this.reloading = true;
    }


      // zoom changed
      /*console.log('zoom changed from ' + oldZoom + ' to ' + newZoom);*/

      let ne = this.osmap.getBounds().getNorthEast();
      let sw = this.osmap.getBounds().getSouthWest();
      let distance = ne.distanceTo(sw);
      this.radius = distance / 2;

      console.log('onZoomChanged check ',  ne, sw, distance, this.radius);


      /*console.log('onZoomChanged: reloading geo-tags? ', this.reloading);*/
      if (this.filter.provider !== null && this.reloading) {
        let latLng = this.osmap.getCenter();
        let pos = [latLng.lat, latLng.lng];
        this.loadGeoTags(pos, this.radius);
        this.reloading = false;
      }

      if (this.filter.provider === null) {
        this.notify.showWarning(
          "Select a city from the filter on the left in order to get geo-tags on the map"
        );
      }
    
  }

  onCenterChanged = function(event) {
    if (!this.osmap) {
      return;
    }
    if (!this.reloading) {
      this.reloading = true;
    }

    // reset the place-name control on the map
    /*
    let inputPlaceControl = this.placeControl.nativeElement.querySelector(
      "input"
    );
    this.renderer.setProperty(inputPlaceControl, "value", "");
    */

    setTimeout(() => {
      let latLng = this.osmap.getCenter();
      /*console.log('onCenterChanged: reloading geo-tags? ', this.reloading);
			console.log('moved from: (' + this.center.lat + ', ' + this.center.lng + ') to: ' + latLng);*/
      if (!this.moving()) {
        return;
      }
      this.center = { lat: latLng.lat, lng: latLng.lng };
      if (this.filter.provider !== null && this.reloading) {
        let pos = [latLng.lat, latLng.lng];
        this.loadGeoTags(pos, this.radius);
        this.reloading = false;
      }
    }, 1000);
  }

  private moving() {
    let latLng = this.osmap.getCenter();
    if (latLng.lat != this.center.lat) {
      return true;
    }
    if (latLng.lng != this.center.lng) {
      return true;
    }
    return false;
  }

  private loadGeoTags(position: number[], distance: number) {
    console.log('loading annotations on the map from center [' + position[0] + ', ' +
      position[1] + '] within distance: ' + distance + ' (meters) - oh and of course filter', this.filter);

    let self = this;  

    this.clearMarkers();
    this.catalogService
      .getGeoDistanceAnnotations(position, distance, this.filter)
      .subscribe(
        (response) => {
          let mapTags = response;

          console.log('mapTags = ', mapTags);

          let relevantCreations = new Map();
          mapTags.forEach((tag) => {
            let m = L.marker([tag.spatial[0], tag.spatial[1]]) as LMarkerPlus;// .addTo(this.osmap);
            // let self = this;
            m.properties = {
              "iri" : tag.iri,
              "name" : tag.name,
              "sources" : tag.sources,
              "target" : self
            };

            m.on("click", self.openInfoWindow.bind(self, m.properties));
/*
            m.on('click', function(e) {

              let target = m.properties.target;
              target.marker = m;
             
              self.nominatimOsmGeocoder.addressLookup(m.properties.name).subscribe(results => {
                    // look outside in order to enrich details for that given place id
                    console.log('Checkpoint Nominatim Results:', results);
                    //if (results[0]) {
                    //  target.marker.properties.address = results[0].formatted_address
                    //}
                  },
                  (error) => {
                    target.notify.showWarning(
                      "Unable to get info for place ID: " + m.properties.iri
                    );
                    target.marker.set("address", "n/a");
                  }
                );
              
              // m.bindPopup(myPopupCode);
              m.on("click", self.openInfoWindow.bind(self, m.properties));
            });*/

            this.markers.push(m);

            // update relavant creations
            for (let i = 0; i < tag.sources.length; i++) {
              let uuid = tag.sources[i].uuid;
              if (!relevantCreations.has(uuid)) {
                relevantCreations.set(uuid, new Set([tag.iri]));
              } else {
                relevantCreations.get(uuid).add(tag.iri);
              }
            }
          });

          this.updateClusters();
          this.onMapChange.emit(relevantCreations);
        },
        (error) => {
          this.notify.showError(
            `There was an error loading geo-tags: ${error}`
          );
        }
      );
  }

  private openInfoWindow(props) {

    console.log('openInfoWindow', props);
    const modalRef = this.modalService.open(MapInfowindowComponent, {
      size: "l",
      centered: true,
    });
    modalRef.componentInstance.properties = props;

    //

    let target = props.target;
    let box = this.osmap.getBounds();

    let boxStr =  box.getNorthEast().lng + ',' + box.getNorthEast().lat+ ',' + box.getSouthWest().lng + ',' + box.getSouthWest().lat;

    this.nominatimOsmGeocoder.addressLookup(props.name, boxStr).subscribe(results => {
          // look outside in order to enrich details for that given place id
          // console.log('Checkpoint Nominatim Results:', results);
          if(results.length > 0 ) {
            console.log('Checkpoint Nominatim Results ----- ', results); // , modalRef);
            modalRef.componentInstance.address = results[0].display_name;
          }
          
          //if (results[0]) {
          //  target.marker.properties.address = results[0].formatted_address
          //}
        },
        (error) => {
          target.notify.showWarning(
            "Unable to get info for place ID: " + props.iri
          );
          target.marker.set("address", "n/a");
        }
      );
 
    
    // need to trigger resize event
    window.dispatchEvent(new Event("resize"));
  }


  private clearMarkers() {
    console.log('clear markers');

    for (let m of this.markers) {
      this.osmap.removeLayer(m);
    }
    this.markers = [];
    if (!!this.markerClusterer) {
      this.osmap.removeLayer( this.markerClusterer);
      this.markerClusterer = false;
    }
  }

  private updateClusters() {

    if(!this.markerClusterer ) {
      this.markerClusterer = L.markerClusterGroup({
        chunkedLoading: true,
        //singleMarkerMode: true,
        spiderfyOnMaxZoom: false
      });
      for (let mi = 0; mi < this.markers.length; mi++) {
        this.markerClusterer.addLayer(this.markers[mi]);
      }

      this.osmap.addLayer(this.markerClusterer);
    }
    /*
    this.markerClusterer = new MarkerClusterer(this.map, this.markers, {
      imagePath:
        "https://developers.google.com/maps/documentation/javascript/examples/markerclusterer/m",
    });
    */
  }
}
