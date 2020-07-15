import { Component, Input, OnInit } from "@angular/core";
import { AppVideoService } from "../../../services/app-video";

@Component({
  selector: "app-shot-reference",
  templateUrl: "app-shot-reference.html",
})
export class AppShotReferenceComponent implements OnInit {
  @Input() shot;

  constructor(private VideoService: AppVideoService) {}

  shot_play() {
    this.VideoService.shot_play(this.shot.shot_num);
  }

  ngOnInit() {}

  isVideo() {
    return this.shot.links &&
      this.shot.links.content &&
      this.shot.links.content.indexOf("type=image") !== -1
      ? false
      : true;
  }
}
