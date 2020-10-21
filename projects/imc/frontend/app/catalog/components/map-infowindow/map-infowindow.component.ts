import { Component, ElementRef, OnInit, Input } from '@angular/core';

@Component({
  selector: 'map-infowindow',
  templateUrl: './map-infowindow.component.html',
  styleUrls: ['./map-infowindow.component.css'],
  providers: []
})
export class MapInfowindowComponent {

  elRef: ElementRef;
  properties: any;
  address: string;
  marker: any;

  constructor(elRef: ElementRef) {
    this.elRef = elRef;
    this.address = "";
  }

  ngOnInit() {
  }
  
  getHtmlContent() {
    //This will return '<p> Text </p>' as a string
    return this.elRef.nativeElement.innerHTML;
  }
  
}