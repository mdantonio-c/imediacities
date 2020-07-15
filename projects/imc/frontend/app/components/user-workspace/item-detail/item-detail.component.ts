import { Component, Input, Output, EventEmitter, OnInit } from "@angular/core";
import { Router } from "@angular/router";
import { NotificationService } from "@rapydo/services/notification";
import { AuthService } from "@rapydo/services/auth";
import { ListsService } from "../../../services/lists.service";

import { environment } from "@rapydo/../environments/environment";

export interface ItemDetail {
  id: string;
  title: string;
  type?: string;
  description?: string;
  thumbnail?: string;
  focus?: boolean;
  listItem?: boolean;
  listId?: string;
  nb_items?: number;
  ref?: any;
  duration?: string;
}

// expected https://{url}?list={listID}&access_token={token}
const VIRTUAL_GALLERY_URL: string = environment.ALL["VIRTUAL_GALLERY_URL"];

@Component({
  selector: "item-detail",
  templateUrl: "./item-detail.component.html",
  styleUrls: ["./item-detail.component.css"],
})
export class ItemDetailComponent implements OnInit {
  @Input() media: ItemDetail;
  @Output() onDelete: EventEmitter<null> = new EventEmitter<null>();
  editable: boolean = false;
  mediaForm: any = {};

  constructor(
    private router: Router,
    private listsService: ListsService,
    private notify: NotificationService,
    private auth: AuthService
  ) {}

  ngOnInit() {
    this.mediaForm["name"] = this.media.title;
    this.mediaForm["description"] = this.media.description;
  }

  disableSaveAs(event) {
    return false;
  }

  route() {
    if (this.media.listItem) {
      // here media.id is item UUID
      // list item conveys with creation model in ref
      let media = this.media.ref;
      if (media.type === "shot" || media.item_type["key"] === "Video") {
        this.router.navigate(["/app/catalog/videos", media.creation_id]);
      } else {
        this.router.navigate(["/app/catalog/images", media.creation_id]);
      }
    } else {
      // here media.id is aventity/nonaventity UUID
      switch (this.media.type) {
        case "nonaventity":
          this.router.navigate(["/app/catalog/images", this.media.id]);
          break;
        case "aventity":
          this.router.navigate(["/app/catalog/videos", this.media.id]);
          break;
      }
    }
  }

  delete() {
    this.onDelete.emit();
  }

  loadListItems() {
    this.listsService.selectList(this.media);
  }

  toggleEdit() {
    this.editable = !this.editable;
  }

  getVGalleryURL() {
    return `${VIRTUAL_GALLERY_URL}?list=${
      this.media.id
    }&access_token=${this.auth.getToken()}`;
  }

  save() {
    console.log(`save updated list <${this.media.title}>`);
    this.listsService.updateList(this.media.id, this.mediaForm).subscribe(
      (response) => {
        this.media.title = this.mediaForm.name;
        this.media.description = this.mediaForm.description;
        console.log(`list <${this.media.title}> updated successfully`);
        this.editable = false;
      },
      (error) => {
        this.notify.showError(error);
      }
    );
  }

  cancel() {
    this.mediaForm["name"] = this.media.title;
    this.mediaForm["description"] = this.media.description;
    this.editable = false;
  }
}
