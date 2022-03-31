import { Component, Input, OnInit, OnChanges } from "@angular/core";
import { Router } from "@angular/router";
import { MediaUtilsService } from "../services/media-utils.service";
import { AuthService } from "@rapydo/services/auth";

@Component({
  selector: "search-result",
  template: "",
})
export class SearchResultComponent implements OnInit, OnChanges {
  @Input() media;

  identifyingTitle: string;
  description: string;
  user: any;

  constructor(private authService: AuthService, private router: Router) {}

  ngOnInit() {
    this.user = this.authService.getUser();
  }

  ngOnChanges() {
    this.identifyingTitle = MediaUtilsService.getIdentifyingTitle(this.media);
    this.description = MediaUtilsService.getDescription(this.media);
  }

  canRevise() {
    return (
      this.user.roles.hasOwnProperty("Reviser") &&
      this.underRevision() &&
      this.user.uuid === this.media._item[0]._revision[0].id
    );
  }

  underRevision() {
    return this.media._item[0]._revision ? true : false;
  }

  disableSaveAs(event) {
    return false;
  }

  route(mediaId: string, mediaType: string) {
    if (mediaType === "nonaventity") {
      const non_av_type =
        this.media.non_av_type.key === "3d-model" ? "models" : "images";
      this.router.navigate([`/app/catalog/${non_av_type}`, mediaId]);
    } else {
      this.router.navigate(["/app/catalog/videos", mediaId]);
    }
  }

  protected getUser() {
    return this.user;
  }
}
