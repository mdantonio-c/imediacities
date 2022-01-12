import { Component, Input, OnInit } from "@angular/core";

@Component({
  selector: "app-media-map-wrapper",
  templateUrl: "app-media-map-wrapper.html",
})
export class AppMediaMapWrapperComponent implements OnInit {
  @Input() locations;
  @Input() media_type;
  @Input() media_owner;
  @Input() shots;

  static map_expanded_label = "Close the map";
  static map_closed_label = "Open the map";

  public map_is_expanded = false;
  public map_label = "";

  constructor() {}

  /**
   * Manage the map display
   */
  map_extend() {
    this.map_is_expanded = !this.map_is_expanded;
    this.map_label = this.map_is_expanded
      ? AppMediaMapWrapperComponent.map_expanded_label
      : AppMediaMapWrapperComponent.map_closed_label;
  }

  ngOnInit() {
    this.map_label = AppMediaMapWrapperComponent.map_closed_label;
  }
}
