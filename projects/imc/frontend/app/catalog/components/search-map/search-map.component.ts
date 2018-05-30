import { Component, Input, ViewChild, OnInit, OnChanges } from '@angular/core';
import { CatalogService } from "../../services/catalog.service";
import { GeoCoder, NguiMapComponent } from '@ngui/map';

const europeCenter = {lat: 45, lng: 14};
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

@Component({
	selector: 'search-map',
	templateUrl: './search-map.component.html',
	styleUrls: ['./search-map.component.css']
})
export class SearchMapComponent implements OnInit, OnChanges {

	/*@Input() current_shot_from_video = false;
	@Input() markers;
	@Input() shots;
	@Input() draggable_markers;
	@Input() clickable_markers;*/
	@Input() countByProviders: any;

	map;
	isLoaded: boolean = false;
	zoom: number;
	center;
	mapStyle = mapStyles.hide;
	radius: number = 1600 * 1000;	// for zoom level 4
	markers: any[] = [];
	mapTags: any[] = [];
	showMapBoundary: boolean = false;
	counters = [];

	@ViewChild(NguiMapComponent) ngMap: NguiMapComponent;

	constructor(
		private catalogService: CatalogService,
		private geoCoder: GeoCoder
	) { }

	ngOnInit() {
		// Center the map on the default
		this.center = europeCenter;
		this.zoom = 4;

		this.loadCountByProvider();
	}

	ngOnChanges() {
		// update counters
		this.loadCountByProvider();
		//  Remove any residual markers
		this.markers.forEach(m => {
			if (m.hasOwnProperty('map')) {
				m.setMap(null)
			}
		});

		//  reset markers
		this.markers = this.markers.slice();
		/*this.fitBounds();*/
	}

	private loadCountByProvider() {
		this.counters = [];
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
	centerCity = function(city) {
		let cityPosition = this.catalogService.getPosition(city);
		var pt = new google.maps.LatLng(cityPosition[0], cityPosition[1]);
		this.map.setCenter(pt);
		this.map.setZoom(14);
	};

	toggleBoundary = function() {
		this.showMapBoundary = !this.showMapBoundary;
		let circle = this.map.shapes[0];
		if (circle === undefined) { return; }
		circle.setVisible(this.showMapBoundary);
	};

	setBoundaryVisible = function(val) {
		this.showMapBoundary = val;
		let circle = this.map.shapes[0];
		if (circle === undefined) { return; }
		circle.setVisible(val);
	};

    onMapReady(map) {
    	/*console.log('map', map);
		console.log('markers', map.markers);*/
        this.map = map;
        /*this.centerEurope();*/
        /*this.fitBounds();*/
    }

	onIdle(event) {
		console.log('map', event.target);
	}

	onMarkerInit(marker) {
		console.log('marker', marker);
	}

	onMapClick(event) {
		console.log('map click');
		/*this.positions.push(event.latLng);
		event.target.panTo(event.latLng);*/
	}

}
