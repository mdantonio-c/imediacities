import { Component, ViewChild, OnInit } from "@angular/core";
import { AppModaleService } from "../../services/app-modale";

@Component({
  selector: "app-modale",
  templateUrl: "app-modale.html",
})
export class AppModaleComponent implements OnInit {
  @ViewChild("content", { static: false }) content;

  public titolo = "";

  constructor(private modalService: AppModaleService) {}

  open(title: string, media_type: string, classes = "") {
    this.title_set(title);
    this.modalService.open(this.content, {
      windowClass: `imc--modal page-type-${media_type} ${classes}`,
    });
  }

  title_set(title) {
    this.titolo = title;
  }

  ngOnInit() {}
}
