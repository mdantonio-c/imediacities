import {
  Component,
  HostBinding,
  Input,
  ElementRef,
  OnInit,
} from "@angular/core";
import { AppAnnotationsService } from "../../services/app-annotations";

@Component({
  selector: "app-note",
  templateUrl: "app-note.html",
})
export class AppNoteComponent implements OnInit {
  @HostBinding("class.notes") notes = true;
  @HostBinding("class.note-expanded") note_expanded = true;

  @Input() note;
  @Input() can_delete = false;

  public icon = "keyboard_arrow_down";
  public popover;

  constructor(
    private element: ElementRef,
    private AnnotationsService: AppAnnotationsService
  ) {}

  delete() {
    if (!this.can_delete) return;
    if (this.note.id) {
      this.AnnotationsService.delete_tag(this.note, this.note.source);
    }
  }
  lock_note() {
    if (!this.can_delete) return;
    if (this.note.id) {
      this.AnnotationsService.update_note_private(this.note, true);
    }
  }
  unlock_note() {
    if (!this.can_delete) return;
    if (this.note.id) {
      this.AnnotationsService.update_note_private(this.note, false);
    }
  }
  toggle() {
    this.icon =
      this.icon === "keyboard_arrow_up"
        ? "keyboard_arrow_down"
        : "keyboard_arrow_up";
    this.note_expanded = this.icon === "keyboard_arrow_up";
  }

  ngOnInit() {
    this.popover = this.AnnotationsService.popover();
    //console.log("note="+JSON.stringify(this.note));
  }
}
