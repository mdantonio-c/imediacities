import {Component, OnInit} from '@angular/core';
import {AppShotsService} from "../../services/app-shots";
import {AppVideoService} from "../../services/app-video";

@Component({
    selector: 'app-media',
    templateUrl: 'app-media.html'
})

export class AppMediaComponent implements OnInit {

    public activeAnnotation: boolean;
    public mediaData: any;
    public shots = [];
    public modale: any;
    public modaleData: any;

    //  Lingua dell'utente
    public user_language = 'xx';

    constructor(private VideoService: AppVideoService, private ShotsService: AppShotsService) {
        this.activeAnnotation = false;
    }

    activeMultiAnnotation(){
        this.activeAnnotation = !this.activeAnnotation;
    }

    selectionModal(modal){
        let shots = this.ShotsService.shots();
        this.modaleData = {
            shots: [shots[3], shots[7]]
        }
        this.modale = modal;
    }

    ngOnInit() {

        this.VideoService.get('cbdebde9-0ccb-40d9-8dbe-bad3d201a3e5', (video) => {this.mediaData = video});
        this.ShotsService.get('cbdebde9-0ccb-40d9-8dbe-bad3d201a3e5',(shots) => {this.shots = shots});


    }

}