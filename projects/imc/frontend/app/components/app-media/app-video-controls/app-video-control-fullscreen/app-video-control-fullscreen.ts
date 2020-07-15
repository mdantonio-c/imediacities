import {
  Component,
  ViewChild,
  ElementRef,
  Output,
  EventEmitter,
  AfterViewInit,
} from "@angular/core";
import { AppVideoControlComponent } from "../app-video-control";
import { AppVideoPlayerComponent } from "../../app-video-player/app-video-player";

@Component({
  selector: "app-video-control-fullscreen",
  templateUrl: "app-video-control-fullscreen.html",
})
export class AppVideoControlFullscreenComponent extends AppVideoControlComponent
  implements AfterViewInit {
  @ViewChild("fullscreen_on", { static: false }) fullscreen_on: ElementRef;
  @ViewChild("fullscreen_off", { static: false }) fullscreen_off: ElementRef;
  @Output() fullscreen: EventEmitter<any> = new EventEmitter();

  fullscreen_stato = "off";
  player = null;

  constructor() {
    super();
  }

  _fullscreen(stato) {
    this.fullscreen_stato = stato;
    this.fullscreen.emit(stato);
  }

  ngAfterViewInit() {
    this.fullscreen_on.nativeElement.addEventListener("click", () => {
      this._fullscreen("on");
    });

    this.fullscreen_off.nativeElement.addEventListener("click", () => {
      this._fullscreen("off");
    });
  }
}
