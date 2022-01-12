import { Component, OnInit, OnChanges, Input } from "@angular/core";
import { AuthService } from "@rapydo/services/auth";
import { is_annotation_owner } from "../../../../decorators/app-annotation-owner";
import { IMC_Annotation } from "../../../../services/app-shots";

@Component({
  selector: "app-modal-all-annotations",
  templateUrl: "app-modal-all-annotations.html",
})
export class AppModalAllAnnotationsComponent implements OnInit, OnChanges {
  @Input() data;
  @Input() media_type: string;
  @Input() readonly media_owner: string;
  @is_annotation_owner() is_annotation_owner;

  public shot;
  private currentUser;

  constructor(private AuthService: AuthService) {}

  /**
   * Is the annotation deletable?
   * @param anno
   */
  anno_is_deletable(anno: IMC_Annotation): boolean {
    return this.is_annotation_owner(
      this.currentUser,
      anno.creator,
      this.media_owner
    );
  }

  ngOnInit() {
    this.currentUser = this.AuthService.getUser();
    this.shot = this.data.shots[0];
  }

  ngOnChanges() {
    this.shot = this.data.shots[0];
  }
}
