import { Injectable } from '@angular/core';
import { NgMapAsyncCallbackApiLoader } from '@ngui/map';

import { environment } from '@rapydo/../environments/environment';

@Injectable()
export class CustomNgMapApiLoader extends NgMapAsyncCallbackApiLoader {
    changeUrl(url) {
        this.config.apiUrl = url;
    }

    setUrl() {
    	const key = environment.ALL['GMAP_KEY'];
    	console.log(key);
    	const url = 'https://maps.google.com/maps/api/js?libraries=places&key='+key;
        this.changeUrl(url);
    }
}