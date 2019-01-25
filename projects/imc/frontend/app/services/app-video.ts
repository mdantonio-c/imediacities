import {Injectable} from '@angular/core';

@Injectable()
export class AppVideoService {

    private _video_component = null;

    constructor() {
    }

    /**
     * Va all'inizio di uno shot
     * @param indice
     */
    shot_play (indice) {
        if (this.video_check()) {
            this._video_component.shot_play(indice)
        }
    }

    /**
     * Recupera lo shot corrente
     * @returns {(() => (() => any) | number) | number}
     */
    shot_current () {
        if (this.video_check()) {
            return this._video_component.shot_current;
        } else {
            return -1
        }
    }

    /**
     * verifica che il video_component sia settato
     * @returns {boolean}
     */
    video_check () {
        return this._video_component !== null;
    }
    /**
     * Imposta il video component
     * @param video
     */
    video_set (video) {
        this._video_component = video;
    }

    fps() {
        if (this._video_component) return this._video_component.fps;
    }
}