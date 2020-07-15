import { Component } from "@angular/core";
import { AppVideoControlComponent } from "../app-video-control";

@Component({
  selector: "app-video-control-play",
  templateUrl: "app-video-control-play.html",
})
export class AppVideoControlPlayComponent extends AppVideoControlComponent {
  constructor() {
    super();
  }

  play() {
    if (this.video.paused) {
      if (this.parent.restart_time !== null) {
        this.video.currentTime = this.parent.restart_time;
        this.parent.restart_time = null;
      }

      this.video.play();
    } else {
      this.video.pause();
    }
  }
}
