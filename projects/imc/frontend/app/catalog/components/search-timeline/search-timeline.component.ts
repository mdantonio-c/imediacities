import { Component, Input } from "@angular/core";
import { decades } from "../../services/catalog.service";

@Component({
  selector: "search-timeline",
  templateUrl: "./search-timeline.component.html",
  styleUrls: ["./search-timeline.component.css"],
})
export class SearchTimelineComponent {
  timelineRange: number[] = decades();
  @Input() countByYears: any;
  @Input() countMissingDate: number = 0;

  constructor() {}
}
