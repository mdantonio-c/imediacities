import { Injectable } from "@angular/core";
import { ApiService } from "@rapydo/services/api";
import { Router } from "@angular/router";
import { NotificationService } from "@rapydo/services/notification";

@Injectable()
export class AppMediaService {
  private _media = null;
  private _media_id = null;
  public _owner = null;

  constructor(
    private api: ApiService,
    private Router: Router,
    private notify: NotificationService
  ) {}

  get(media_id, endpoint, cb) {
    if (!cb || typeof cb !== "function") {
      console.log("AppMediaService", "Callback mancante");
      return;
    }

    this.api.get(endpoint + "/" + media_id).subscribe(
      (response) => {
        this._media = response[0];
        this._media_id = media_id;
        this._owner = this._media._item[0]._ownership[0];

        cb(this._media);
      },
      (err) => {
        this.Router.navigate(["/404"]);
        console.log("err", err);
      }
    );
  }

  owner() {
    return this._owner;
  }

  media() {
    return this._media;
  }

  media_id() {
    return this._media_id;
  }

  type() {
    return this._media.type === "aventity" ? "video" : "image";
  }

  revisionState(): string {
    return this._media._item[0]._revision
      ? this._media._item[0]._revision[0].state.key
      : "";
  }

  updatePublicAccess(newVal: boolean) {
    this.api
      .put(this.type() + "s/" + this.media_id() + "/item", {
        public_access: newVal,
      })
      .subscribe(
        (response) => {
          this._media._item[0].public_access = newVal;
        },
        (err) => {
          console.error("Error updating public access: ", err);
          this.notify.showError("The update of public access flag is failed");
        }
      );
  }
}
