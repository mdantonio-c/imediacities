import { Component, ElementRef, OnInit, Input } from '@angular/core';

@Component({
  selector: 'map-infowindow',
  templateUrl: './map-infowindow.component.html',
  styleUrls: ['./map-infowindow.component.css']
})
export class MapInfowindowComponent {

  elRef: ElementRef;

  constructor(elRef: ElementRef) {
    this.elRef = elRef;
  }

  ngOnInit() {
  }
  
  getHtmlContent() {
    //This will return '<p> Text </p>' as a string
    return this.elRef.nativeElement.innerHTML;
  }
}