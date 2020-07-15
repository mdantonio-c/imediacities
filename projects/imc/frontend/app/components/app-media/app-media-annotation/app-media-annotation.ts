import { Component, ElementRef, Input, OnInit } from "@angular/core";
import { AppAnnotationsService } from "../../../services/app-annotations";

@Component({
  selector: "app-media-annotation",
  templateUrl: "app-media-annotation.html",
})
export class AppMediaAnnotationComponent implements OnInit {
  @Input() annotation;
  @Input() clickable;
  @Input() can_delete;
  @Input() delete_fn;
  @Input() disable_confirmation = false;
  @Input() tag = false;

  public popover;

  constructor(
    private element: ElementRef,
    private AnnotationsService: AppAnnotationsService
  ) {}

  delete() {
    if (this.tag) return;
    if (!this.can_delete) return;
    if (this.annotation.id) {
      this.AnnotationsService.delete_tag(
        this.annotation,
        this.annotation.source
      );
    } else if (this.delete_fn) {
      this.delete_fn(this.annotation);
    }
  }

  cancella_senza_popover() {
    if (this.disable_confirmation === true) {
      this.delete();
    }
  }

  ngOnInit() {
    let classe = "badge-termtag";
    if (this.annotation.group === "location") {
      classe = "badge-geotag";
    }

    if (!this.tag && this.annotation.creator_type !== "user") {
      classe += "--auto";
    }

    /*if (this.tag) {
            classe += '--count';
        }*/

    this.element.nativeElement.querySelector("span").classList.add(classe);
    this.popover = this.AnnotationsService.popover();
  }
}
