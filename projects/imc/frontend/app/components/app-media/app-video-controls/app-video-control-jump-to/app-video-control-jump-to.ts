import { Component, OnInit } from "@angular/core";
import { AppVideoControlComponent } from "../app-video-control";

@Component({
  selector: "app-video-control-jump-to",
  templateUrl: "app-video-control-jump-to.html",
})
export class AppVideoControlJumpToComponent extends AppVideoControlComponent {
  jump_to_value = 0;

  constructor() {
    super();
  }

  jump_to() {
    if (this._value_is_valid()) {
      this.parent.jump_to(this.jump_to_value, true);
    }
  }

  _value_is_valid() {
    return !isNaN(this.jump_to_value);
  }
}
