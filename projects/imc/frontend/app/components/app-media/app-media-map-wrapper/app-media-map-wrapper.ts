import {Component, Input, OnInit} from '@angular/core';
import {AppMediaMapComponent} from "../app-media-map/app-media-map";

@Component({
    selector: 'app-media-map-wrapper',
    templateUrl: 'app-media-map-wrapper.html'
})

export class AppMediaMapWrapperComponent implements OnInit {
    
    @Input() shots;

    static map_expanded_label = 'Close the map';
    static map_closed_label = 'Open the map';

    public map_is_expanded = false;
    public map_label = 'Open the';

    constructor() {
    }

    /**
     * Gestisce la visualizzazione della mappa
     */
    map_extend() {
        this.map_is_expanded = !this.map_is_expanded;
        this.map_label = this.map_is_expanded ? AppMediaMapWrapperComponent.map_expanded_label: AppMediaMapWrapperComponent.map_closed_label;
    }

    ngOnInit() {
        this.map_label = AppMediaMapWrapperComponent.map_closed_label;
    }
}