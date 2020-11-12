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
  constructor() {}
}
