import { Component, OnInit, Output, EventEmitter } from "@angular/core";
import { AppVideoControlComponent } from "../app-video-control";

@Component({
  selector: "app-video-control-advanced",
  templateUrl: "app-video-control-advanced.html",
})
export class AppVideoControlAdvancedComponent extends AppVideoControlComponent {
  advanced_is_visible = false;
  @Output() advanced_show: EventEmitter<boolean> = new EventEmitter();

  constructor() {
    super();
  }

  advanced_set() {
    this.advanced_is_visible = !this.advanced_is_visible;
    this.advanced_show.emit(this.advanced_is_visible);
  }
}
