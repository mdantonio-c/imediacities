import { Component, OnInit } from '@angular/core';
import { AppVideoControlComponent } from "../app-video-control";

@Component({
    selector: 'app-video-control-switch',
    templateUrl: 'app-video-control-switch.html'
})
export class AppVideoControlSwitchComponent extends AppVideoControlComponent {

    source = null;
    orf_load = false;
    orf_not_available = false;

    constructor() {
        super();
    }

    ngOnInit() {
        super.ngOnInit();
        this.source = this.video.currentSrc.split('?')[0];

        if (this.source) {
            const visibilita_componente = (headers) => {
                this.orf_not_available = headers.includes('json');
            };
            this.type_check(this.source, visibilita_componente);
        }
    }

    /**
     * Setta il tipo di video da visualizzare
     */
    source_set() {

        this.orf_load = !this.orf_load;
        const type = this.orf_load ? 'orf' : 'video';

        let paused = this.video.paused;
        let currentTime = this.video.currentTime;
        this.video.pause();

        this.video.src = this.source_create(type);

        this.video.load();
        this.video.currentTime = currentTime;

        if (!paused) {
            this.video.play();
        }
    }

    /**
     * Crea l'url per un formato di video
     * @param type {string} il formato di video di cui ottenere l'url
     * @returns {string}
     */
    source_create(type) {
        return `${this.source}?type=${type}`
    }

    /**
     * Verifica se esiste il video nel formato specificato da type
     * @param url {string} l'url del video
     * @param callback funzione da eseguire alla ricezione degli header
     * @param {string} type il tipo da verificare
     */
    type_check(url, callback, type = 'orf') {

        const request = new XMLHttpRequest();
        //  todo con un HEAD verrebbe meglio
        const method = 'HEAD';

        request.onreadystatechange = () => {
            //  readyState 2 => headers ricevuti
            if (request.readyState === 2) {
                let headers = request.getAllResponseHeaders();
                callback(headers);
                request.abort();
            }
        };

        request.open(method, this.source_create(type));
        request.send();
    }

}