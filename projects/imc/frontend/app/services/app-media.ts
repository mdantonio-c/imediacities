import {Injectable} from '@angular/core';
import {ApiService} from '/rapydo/src/app/services/api';
import {ProviderToCityPipe} from "../pipes/ProviderToCity";
import {GeoCoder} from '@ngui/map';

@Injectable()
export class AppMediaService {

    private _media = null;
    public _owner = null;

    constructor (private api: ApiService, private geoCoder: GeoCoder, private ProviderToCity: ProviderToCityPipe) {

    }

    get (media_id, cb) {

        if (!cb || typeof cb !== 'function') {
            console.log("AppMediaService", "Callback mancante");
            return
        }

        this.api.get(
            'videos',
            media_id
        ).subscribe(
            response => {

                this._media = response.data[0];
                this._owner = this._media.relationships.item[0].relationships.ownership[0];

                //  Cerco coordinate della città della cineteca cui appartiene il media
                if (this._owner && this._owner.attributes && this._owner.attributes.shortname) {
                    this.coordinates_find(
                        { address: this.ProviderToCity.transform(this._owner.attributes.shortname) },
                        (result) => {
                            this.owner_coordinates_add(result)
                        }
                    )
                }


                cb(this._media);
            },
            err => {
                console.log("err", err);
            }
        );

    }

    owner () {
        return this._owner
    }

    owner_coordinates_add (result) {
        this._owner.location = {
            lat: result.geometry.location.lat(),
            lng: result.geometry.location.lng()
        };
    }

    media () {
        return this._media;
    }

    type () {
        return this._media.type === 'aventity' ? 'video' : 'picture';
    }

    private coordinates_find (options, cb) {

        this.geoCoder.geocode(
            options
        ).subscribe(
            results => {
                cb(results[0]);
            },
            null
        );
    }

}