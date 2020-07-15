import { Component, OnInit } from "@angular/core";

@Component({
  selector: "app-media-commenti",
  templateUrl: "app-media-commenti.html",
})
export class AppMediaCommentiComponent implements OnInit {
  public addReply = false;
  public reply = false;
  constructor() {}

  mostraTextarea() {
    this.addReply = !this.addReply;
  }

  mostraRisposte() {
    this.reply = !this.reply;
  }

  ngOnInit() {}
}
