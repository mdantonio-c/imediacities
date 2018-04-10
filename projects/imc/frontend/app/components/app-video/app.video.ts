// test
import { Component, Input, OnInit } from '@angular/core';
import {HttpClient} from '@angular/common/http';

@Component({
    selector: 'appVideo',
    providers: [],
    templateUrl: './app.video.html',
})
export class AppVideoComponent implements OnInit {

    public videoData = null;
    public videoMeta : any;

    constructor(private http: HttpClient) { }


    ngOnInit() {
        console.log('onInit',' http://192.168.2.37:8080/api/videos/cbdebde9-0ccb-40d9-8dbe-bad3d201a3e5');

        this.http.get(
            'http://192.168.2.37:8080/api/videos/cbdebde9-0ccb-40d9-8dbe-bad3d201a3e5'
        )
            .toPromise()
            .then(
                response => {
                    this.videoData = response['Response'].data[0];
                    this.videoMeta = response['Meta'];
                    console.log("typeof response",  typeof response);
                    console.log("response",  response);
                    // console.log("response",  response.Meta);
                    // console.log("response",  response.Response);
                },
                err => {
                    alert('ops');
                    console.log("err",  err);
                }
            )

    }
}