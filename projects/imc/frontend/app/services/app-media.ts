import { Injectable } from '@angular/core';
import { ApiService } from '/rapydo/src/app/services/api';
import { Router } from '@angular/router';

@Injectable()
export class AppMediaService {

    private _media = null;
    private _media_id = null;
    public _owner = null;

    constructor(
        private api: ApiService,
        private Router: Router) {

    }

    get(media_id, endpoint, cb) {

        if (!cb || typeof cb !== 'function') {
            console.log("AppMediaService", "Callback mancante");
            return
        }

        this.api.get(
            endpoint,
            media_id
        ).subscribe(
            response => {

                this._media = response.data[0];
                this._media_id = media_id;
                this._owner = this._media.relationships.item[0].relationships.ownership[0];

                cb(this._media);

            },
            err => {
                this.Router.navigate(['/404']);
                console.log("err", err);
            }
        );
    }

    owner() {
        return this._owner
    }


    media() {
        return this._media;
    }

    media_id() {
        return this._media_id;
    }


    type() {
        return this._media.type === 'aventity' ? 'video' : 'image';
    }

    revisionState(): string {
        return (this._media.relationships.item[0].relationships.revision) ?
            this._media.relationships.item[0].relationships.revision[0].attributes.state.key : '';
    }

}