
import {Injectable} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {Observable} from 'rxjs';
import {map} from 'rxjs/operators';

// osm nominatim geocoding stuff
export class NominatimResponse {
  constructor(
    public latitude: number,
    public longitude: number,
    public displayName: string
  ) { }
}
export const BASE_NOMINATIM_URL: string = 'nominatim.openstreetmap.org';


@Injectable()
export class NominatimService {

  constructor(private http: HttpClient) {
  }

  addressLookup(req?: any, box?: any): Observable<any> {
    let url = `https://${BASE_NOMINATIM_URL}/search?format=json&q=${req}&viewbox=${box}&bounded=1`;
    let ret = this.http
    .get(url)
    return ret;
  }

  reverse(lat:any, lng:any): Observable<any> {
    let url = `https://${BASE_NOMINATIM_URL}/reverse?format=json&lat=${lat}&lon=${lng}`;
    let ret = this.http
    .get(url)
    return ret;
    /*.pipe(
      map((data: any[]) => data.map((item: any) => new NominatimResponse(
        item.lat,
        item.lon,
        item.display_name
        ))
      )
    )
    */
  }

}