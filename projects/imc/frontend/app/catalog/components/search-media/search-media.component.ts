import { Component } from "@angular/core";
import { SearchResultComponent } from "../search-result.component";

@Component({
  selector: "search-media",
  templateUrl: "./search-media.component.html",
  styleUrls: ["./search-media.component.scss"],
})
export class SearchMediaComponent extends SearchResultComponent {}
