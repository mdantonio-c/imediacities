import { Component, OnInit, OnChanges, Input } from "@angular/core";
import { AuthService } from "@rapydo/services/auth";
import { is_annotation_owner } from "../../../../decorators/app-annotation-owner";

@Component({
  selector: "app-modal-all-annotations",
  templateUrl: "app-modal-all-annotations.html",
})
export class AppModalAllAnnotationsComponent implements OnInit, OnChanges {
  @Input() data;
  @Input() media_type: string;
  @is_annotation_owner() is_annotation_owner;

  public shot;
  private _current_user;

  constructor(private AuthService: AuthService) {}

  anno_is_deletable(anno) {
    return this.is_annotation_owner(this._current_user, anno.creator);
  }

  ngOnInit() {
    this._current_user = this.AuthService.getUser();
    this.shot = this.data.shots[0];
  }

  ngOnChanges() {
    this.shot = this.data.shots[0];
  }

  removeLink(link) {
    console.log("remove link", link);
  }

  canRemoveLink(link) {
    return true;
  }
}
