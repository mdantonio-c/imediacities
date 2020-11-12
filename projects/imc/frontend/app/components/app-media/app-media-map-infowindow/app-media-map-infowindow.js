import { Component, ElementRef, OnInit, Input } from '@angular/core';

@Component({
  selector: 'app-media-map-infowindow',
  templateUrl: './app-media-map-infowindow.component.html',
  styleUrls: ['./app-media-map-infowindow.component.css'],
  providers: []
})
export class AppMediaMapInfowindowComponent {

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