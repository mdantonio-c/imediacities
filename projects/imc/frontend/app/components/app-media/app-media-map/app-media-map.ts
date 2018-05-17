import {Component, OnInit} from '@angular/core';

@Component({
    selector: 'app-media-map',
    templateUrl: 'app-media-map.html'
})

export class AppMediaMapComponent implements OnInit {
    public expandedMap = false;
    constructor() {
    }

    expandMap() {
      this.expandedMap = !this.expandedMap;
    }

    ngOnInit() {
    }
}