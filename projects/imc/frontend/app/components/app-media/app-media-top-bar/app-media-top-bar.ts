import { Component, Input, OnInit, OnChanges } from "@angular/core";
import { Location } from "@angular/common";
import { AuthService } from "@rapydo/services/auth";

@Component({
  selector: "app-media-top-bar",
  templateUrl: "app-media-top-bar.html",
  styleUrls: ["./app-media-top-bar.css"],
})
export class AppMediaTopBarComponent implements OnInit, OnChanges {
  @Input() item_type: string;
  @Input() item_id: string;
  @Input() is_3d_model: boolean = false;
  icon = "";
  label = "";
  user: any;

  constructor(private _location: Location, private authService: AuthService) {}

  backClicked() {
    this._location.back();
  }

  media_type_set() {
    if (this.item_type === "video") {
      this.icon = "videocam";
      this.label = "VIDEO";
    } else if (this.item_type === "image") {
      this.icon = this.is_3d_model ? "view_in_ar" : "image";
      this.label = this.is_3d_model ? "3D MODEL" : "PHOTO";
    }
  }

  ngOnInit() {
    this.user = this.authService.getUser();
  }

  ngOnChanges() {
    this.media_type_set();
  }
}
