import { Component } from "@angular/core";
import { SearchResultComponent } from "../search-result.component";

@Component({
  selector: "search-media-tag",
  templateUrl: "./search-media-tag.component.html",
  styleUrls: ["./search-media-tag.component.css"],
})
export class SearchMediaTagComponent extends SearchResultComponent {
  ngOnChanges() {}

  // override
  canRevise() {
    return (
      super.getUser().roles.hasOwnProperty("Reviser") &&
      this.underRevision() &&
      super.getUser().uuid === this.media.source.reviser.uuid
    );
  }

  // override
  underRevision() {
    return this.media.source.reviser ? true : false;
  }
}
