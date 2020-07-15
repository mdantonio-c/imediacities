import { Component } from "@angular/core";
import { SearchResultComponent } from "../search-result.component";

@Component({
  selector: "search-thumbnail",
  templateUrl: "./search-thumbnail.component.html",
  styleUrls: ["./search-thumbnail.component.css"],
})
export class SearchThumbnailComponent extends SearchResultComponent {}
