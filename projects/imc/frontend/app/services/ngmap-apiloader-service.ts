import { Injectable } from '@angular/core';
import { NgMapAsyncCallbackApiLoader } from '@ngui/map';

@Injectable()
export class CustomNgMapApiLoader extends NgMapAsyncCallbackApiLoader {
    changeUrl(url) {
        this.config.apiUrl = url;
    }
}