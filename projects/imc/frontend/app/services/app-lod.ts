import {Injectable} from '@angular/core';
import {HttpClient} from '@angular/common/http';

@Injectable()
export class AppLodService {

    constructor(private http: HttpClient) {
    }

    search (search_key, language = 'en', limit = '50', type = 'item') {
        const url = `https://www.wikidata.org/w/api.php`;
        const query_string = `?action=wbsearchentities&format=json&search=${search_key}&type=${type}&limit=${limit}&language=${language}`;

        return this.http.jsonp(url + query_string, 'callback')
            .map(
                res => AppLodService.jsonp_unwrap(res)
            )
            .toPromise()
    }

    static jsonp_unwrap (res) {
        return res;
    }
}