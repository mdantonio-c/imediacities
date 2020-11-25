import { Component, ElementRef, OnInit, Input } from '@angular/core';
import { CommonModule } from '@angular/common'; 

@Component({
  selector: 'app-media-map-infowindow',
  templateUrl: './app-media-map-infowindow.html',
  styleUrls: ['./app-media-map-infowindow.css'],
  providers: []
})
export class AppMediaMapInfowindowComponent {

  elRef: ElementRef;
  properties: any;
  address: string;
  popover: any;
  marker: any;
  marker_edit: any;
  media_type: any;
  iw: boolean;
  iw_add: boolean;
  info_window_data : any;

  appMediaMapComponentRef : any;

  constructor(elRef: ElementRef) {
    this.elRef = elRef;
    this.address = "";
    this.iw = false;
    this.iw_add = true;
    this.popover = {};
    this.info_window_data = {};
  }

  ngOnInit() {
  }
  
  getHtmlContent() {
    //This will return '<p> Text </p>' as a string
    return this.elRef.nativeElement.innerHTML;
  }

  marker_edit_save() {
    this.appMediaMapComponentRef.marker_edit_save();
  }

  marker_delete(wat: any) {
    this.appMediaMapComponentRef.marker_delete(wat);
  }

  marker_edit_close() {
    this.appMediaMapComponentRef.marker_edit_close();
  }
  
}