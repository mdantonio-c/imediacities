import {
  Component,
  Input,
  AfterViewInit,
  ViewChild,
  ElementRef,
} from "@angular/core";
import { AuthService } from "@rapydo/services/auth";

@Component({
  selector: "app-3d-model",
  templateUrl: "app-3d-model.html",
  styleUrls: ["app-3d-model.css"],
})
export class App3dModelComponent implements AfterViewInit {
  @Input() data;

  constructor(private auth: AuthService) {}

  ngAfterViewInit() {}
}
