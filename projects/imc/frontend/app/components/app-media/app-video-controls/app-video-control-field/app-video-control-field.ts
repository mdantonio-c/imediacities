import { Component, Input, OnInit } from "@angular/core";

@Component({
  selector: "app-video-control-field",
  templateUrl: "app-video-control-field.html",
})
export class AppVideoControlFieldComponent implements OnInit {
  @Input() parent;

  static lock_icon_open = "lock_open";
  static lock_icon_closed = "lock";
  locked = false;
  lock_icon = "";
  public input_value = 0;

  constructor() {}

  public value() {
    return this.input_value;
  }

  frame_copia(event) {
    if (this.locked) {
      return;
    }

    this.input_value = this.parent.frame_current();
    event.target.value = this.input_value;
    event.target.dispatchEvent(new Event("input"));
  }

  frame_lock() {
    this.locked = !this.locked;
    this.lock_icon = this.locked
      ? AppVideoControlFieldComponent.lock_icon_closed
      : AppVideoControlFieldComponent.lock_icon_open;
  }

  ngOnInit() {
    this.lock_icon = AppVideoControlFieldComponent.lock_icon_open;
  }
}
