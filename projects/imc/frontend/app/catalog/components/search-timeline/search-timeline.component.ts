import { Component, Input } from "@angular/core";

@Component({
  selector: "search-timeline",
  templateUrl: "./search-timeline.component.html",
  styleUrls: ["./search-timeline.component.css"],
})
export class SearchTimelineComponent {
  timelineRange: number[] = [
    1890,
    1900,
    1910,
    1920,
    1930,
    1940,
    1950,
    1960,
    1970,
    1980,
    1990,
  ];
  @Input() countByYears: any;
  @Input() countMissingDate: number = 0;

  constructor() {}
}
