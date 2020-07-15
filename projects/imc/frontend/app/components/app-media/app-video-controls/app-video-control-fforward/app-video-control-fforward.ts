import { Component, OnInit } from "@angular/core";

import { AppVideoControlComponent } from "../app-video-control";
import { AppVideoControlsFastPlayService } from "../../../../services/app-video-controls-fast-play";

@Component({
  selector: "app-video-control-fforward",
  templateUrl: "app-video-control-fforward.html",
})
export class AppVideoControlFforwardComponent extends AppVideoControlComponent {
  stato = 0;

  constructor(
    public AppVideoControlsFastPlay: AppVideoControlsFastPlayService
  ) {
    super();
  }

  fforward() {
    this.AppVideoControlsFastPlay.fast_play(1, this.video);
  }

  onplay() {
    this.parent.spinner_prevent = false;
    this.AppVideoControlsFastPlay.stop();
  }

  onbegin() {
    this.parent.spinner_prevent = false;
    this.AppVideoControlsFastPlay.stop();
  }

  onended() {
    this.parent.spinner_prevent = false;
    this.AppVideoControlsFastPlay.stop();
  }

  onseeked() {
    this.parent.spinner_prevent =
      this.AppVideoControlsFastPlay.interval !== null;
  }

  onseeking() {
    this.parent.spinner_prevent =
      this.AppVideoControlsFastPlay.interval !== null;
  }
}
