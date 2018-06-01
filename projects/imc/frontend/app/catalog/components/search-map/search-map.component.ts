import { 
	Component,
	Input,
	Output,
	ViewChild,
	ElementRef,
	EventEmitter,
	ChangeDetectorRef,
	OnInit, OnChanges
} from '@angular/core';
import { CatalogService, SearchFilter } from "../../services/catalog.service";
import { GeoCoder, NguiMapComponent } from '@ngui/map';
import { NotificationService } from '/rapydo/src/app/services/notification';

const europeCenter = { lat: 45, lng: 14 };
const mapStyles = {
	default: null,
	hide: [{
		featureType: 'poi.business',
		stylers: [{
			visibility: 'off'
		}]
	}, {
		featureType: 'transit',
		elementType: 'labels.icon',
		stylers: [{
			visibility: 'off'
		}]
	}]
};
interface GeoMarker {
	iri: string;
	name: string;
	address: string;
	sources: string[];
	position: LatLng;
};
interface LatLng {
	lat: number;
	lng: number;
};
export interface MediaTag {
	annotations: any[];
	source: MediaSource;
};
export interface MediaSource {
	external_ids: string[];
	provider: string;
	rights_status: string;
	title: string;
	type: string;
	uuid: string;
	year: string;
};

@Component({
	selector: 'search-map',
	templateUrl: './search-map.component.html',
	styleUrls: ['./search-map.component.css']
})
export class SearchMapComponent implements OnInit, OnChanges {

	@Input() countByProviders: any;
	@Input() filter: SearchFilter;
	@Output() onMapChange: EventEmitter<any> = new EventEmitter<string>();

	map;
	private zoom;
	/*isLoaded: boolean = false;*/
	mapStyle = mapStyles.hide;
	radius: number = 1600 * 1000;	// for zoom level 4
	markers: GeoMarker[] = [];
	showMapBoundary: boolean = false;
	counters = [];
	autocomplete: any;

	@ViewChild(NguiMapComponent) private ngMap: NguiMapComponent;
	@ViewChild('customControl') private customControl: ElementRef;
	@ViewChild('placeControl') private placeControl: ElementRef;

	marker: GeoMarker = {
		iri: null,
		name: null,
		address: null,
		sources: [],
		position: null
	};

	constructor(
		private catalogService: CatalogService,
		private geoCoder: GeoCoder,
		private ref: ChangeDetectorRef,
		private notify: NotificationService
	) { }

	initialized(autocomplete: any) {
		this.autocomplete = autocomplete;
	}

	placeChanged(place) {
		if (place === undefined) { return; }
		this.map.setCenter(place.geometry.location);
		this.map.fitBounds(place.geometry.viewport);
		this.ref.detectChanges();
	}

	ngOnInit() {
		/*console.log('ngOnInit');*/
		this.loadCountByProvider();
		if (this.filter.provider != null) {
			// load geo-tags for this provider
		}
	}

	ngOnChanges() {
		/*console.log('ngOnChanges');*/
		// update counters
		if (!this.filter.provider) {
			this.loadCountByProvider();
		}
		//  Remove any residual markers
		/*this.markers.forEach(m => {
			if (m.hasOwnProperty('map')) {
				m.setMap(null)
			}
		});

		//  reset markers
		this.markers = this.markers.slice();*/
		/*this.fitBounds();*/
	}

	private loadCountByProvider() {
		this.counters = [];
		if (this.countByProviders === undefined) { return; }
		/*console.log("countByProviders", this.countByProviders);*/
		for (let key of Object.keys(this.countByProviders)) {
			let city = this.catalogService.getProviderCity(key);
			let entry = {
				name: city.name,
				position: city.position,
				counter: this.countByProviders[key],
				provider: key
			};
			this.counters.push(entry);
		}
	}

	centerEurope = function() {
		let pt = new google.maps.LatLng(europeCenter.lat, europeCenter.lng);
		this.map.setCenter(pt);
		this.map.setZoom(4);
	};

	/**
	 * Center the map on a given city.
	 * @param city - Archive ID (e.g. CCB)
	 */
	centerCity = function(provider) {
		if (this.map === undefined) {
			console.warn('The center cannot be set because the map is undefined.');
			return;
		}
		let cityPosition = this.catalogService.getProviderPosition(provider);
		var pt = new google.maps.LatLng(cityPosition[0], cityPosition[1]);
		this.map.setCenter(pt);
		this.map.setZoom(14);
		this.center = { lat: cityPosition[0], lng: cityPosition[1] };
	};

	toggleBoundary = function() {
		this.showMapBoundary = !this.showMapBoundary;
	};

	onMapReady(map) {
		/*console.log('onMapReady');*/
		/*console.log('map', map);*/

		// add custom controls
		map.controls[google.maps.ControlPosition.TOP_RIGHT].push(this.customControl.nativeElement);
		map.controls[google.maps.ControlPosition.TOP_LEFT].push(this.placeControl.nativeElement);

		this.map = map;
		this.zoom = map.getZoom();
		(this.filter.provider != null) ? this.centerCity(this.filter.provider) : this.centerEurope();
		/*this.fitBounds();*/
		/*console.log('markers', map.markers);*/
	}

	onIdle(event) {
		console.log('map', event.target);
	}

	onMarkerInit(marker) {
		console.log('marker', marker);
	}

	onZoomChanged(event) {
		/*console.log(event);*/
		let oldZoom = this.zoom;
		let newZoom = event.target.zoom;
		if (newZoom !== oldZoom) {
			// zoom changed
			console.log('zoom changed from ' + oldZoom + ' to ' + newZoom);
			// fit the circle radius properly
			this.radius = Math.pow(2, oldZoom - newZoom) * this.radius;
			// console.log('new radius: ' + sc.radius + ' meters');
			this.zoom = newZoom;
			if (this.filter.provider !== null) {
				let pos = [this.map.getCenter().lat(), this.map.getCenter().lng()];
				this.loadGeoTags(pos, this.radius);
			}
		}
	}


	onCenterChanged(event) {
		/*console.log('center changed');*/
	}

	/**
     * Show InfoWindow for a marker
     * @param event
     * @param pos
     */
	showInfoWindow({ target: marker }, geoMarker) {
		this.marker = geoMarker;
		this.geoCoder.geocode({
			'placeId': geoMarker.iri
		}).subscribe(results => {
			// look outside in order to enrich details for that given place id
			if (results[0]) {
				this.marker.address = results[0].formatted_address;
			}
		}, error => {
			this.notify.showWarning('Unable to get info for place ID: ' + geoMarker.iri);
		});

		marker.nguiMapComponent.openInfoWindow('tag-iw', marker);
	}

	private loadGeoTags(position: number[], distance: number) {
		/*console.log('loading annotations on the map from center [' + position[0] + ', ' +
			position[1] + '] within distance: ' + distance + ' (meters)');*/
		this.clearMarkers();
		this.catalogService.getGeoDistanceAnnotations(position, distance, this.filter).subscribe(response => {
			let mapTags = response["Response"].data;
			let relevantCreations = new Map();
			mapTags.forEach(tag => {
				/*console.log(tag);*/
				let m = {
					iri: tag.iri,
					name: tag.name,
					address: null,
					sources: tag.sources,
					position: {
						lat: tag.spatial[0],
						lng: tag.spatial[1]
					}
				}
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
			
		}, error => {
			this.notify.extractErrors(`There was an error loading geo-tags: ${error}`, this.notify.ERROR);
		});
	}

	private clearMarkers() {
		// TODO
	}

	private updateClusters() {
		// TODO
	}

}
