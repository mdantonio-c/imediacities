import {
  Component,
  Input,
  ChangeDetectionStrategy,
  Output,
  EventEmitter,
} from "@angular/core";
import { User } from "@rapydo/types";

@Component({
  selector: "customlinks",
  templateUrl: "./custom.navbar.links.html",
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class CustomNavbarComponent {
  @Input() user: User;
  @Output() onClick: EventEmitter<null> = new EventEmitter<null>();

  constructor() {}

  public collapse() {
    this.onClick.emit();
  }
}

@Component({
  selector: "custombrand",
  templateUrl: "./custom.navbar.brand.html",
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class CustomBrandComponent {
  // public url = "https://imediacities.eu";
  // public image = "IMC-Logo-transp.png";
  // public alt = "I-MediaCities logo";

  public url = "https://www.darsenaravenna.it";
  public image = "DR_logo_04.png";
  public alt = "DARE logo";

  constructor() {}
}
