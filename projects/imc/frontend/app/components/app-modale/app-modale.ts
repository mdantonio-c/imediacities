import { Component, ViewChild, OnInit } from "@angular/core";
import { AppModaleService } from "../../services/app-modale";

@Component({
  selector: "app-modale",
  templateUrl: "app-modale.html",
})
export class AppModaleComponent {
  @ViewChild("content", { static: false }) content;

  title = "";

  constructor(private modalService: AppModaleService) {}

  open(title: string, mediaType: string, classes = "") {
    this.title_set(title);
    this.modalService.open(this.content, {
      windowClass: `imc--modal page-type-${mediaType} ${classes}`,
    });
  }

  title_set(title: string) {
    this.title = title;
  }
}
