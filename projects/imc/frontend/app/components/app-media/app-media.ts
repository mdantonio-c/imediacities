import {Component, OnInit, ViewChild} from '@angular/core';
import {AppShotsService} from "../../services/app-shots";
import {AppVideoService} from "../../services/app-video";
import {AppModaleComponent} from "../app-modale/app-modale";
import {AppVideoPlayerComponent} from "./app-video-player/app-video-player";

/**
 * Componente per la visualizzazione del media
 */
@Component({
    selector: 'app-media',
    templateUrl: 'app-media.html'
})

export class AppMediaComponent implements OnInit {

    /**
     * Riferimento al componente AppModale
     */
    @ViewChild('appModale') appModale: AppModaleComponent;
    /**
     * Riferimento al componente AppVideoPlayer
     */
    @ViewChild('appVideo') appVideo: AppVideoPlayerComponent;

    /**
     * Consente di visualizzare lo strumento per la selezione multipla degli shot
     */
    public multi_annotations_is_active: boolean = false;
    /**
     * Riceve i risultati della chiamata al servizio media
     */
    public media: any;
    /**
     * Oggetto da visualizzare nel corpo della modale
     * @type {{type: string; data: {}}}
     */
    public modale = {
        /**
         * Nome del componente da visualizzare
         */
        type: '',
        /**
         * Dati da passare al componente
         */
        data: {}
    };
    public locations;
    /**
     * Riceve i risultati della chiamata al servizio shots
     * @type {any[]}
     */
    public shots = [];
    public shots_attivi = [];
    /**
     * Lingua dell'utente da legare in futuro all'utente loggato
     * @type {string}
     */
    public user_language = 'it';

    constructor(private VideoService: AppVideoService, private ShotsService: AppShotsService) {}

    /**
     * Modifica la visibilità dello strumento per la selezione multipla degli shot
     * e ne resetta lo stato deselezionando tutti
     */
    multi_annotations_toggle(){
        this.multi_annotations_is_active = !this.multi_annotations_is_active;
        this.shots_attivi_reset();
    }

    /**
     * Apre una modale visualizzando al suo interno il compontente coi dati ricevuti
     * @param componente Configurazione del componente daq visualizzare nella modale
     */
    modal_show (componente){

        //  fermo il video principale
        this.appVideo.video.pause();

        this.modale.type = componente.modale;
        this.modale.data = componente.data;

        this.appModale.open(componente.titolo, this.VideoService.type(), componente.classe);

    }

    /**
     * Apre una modale visualizzando al suo interno il componente coi dati ricevuti
     * Inserisce nei dati da visualizzare gli shots selezionati
     * @param evento Evento richiamante
     * @param componente Componente selezionato
     */
    modal_show_multi (evento, componente) {

        let data = this.shots_attivi.reduce((acc, value, index) => {
            if (value) {
                acc.push(this.shots[index])
            }
            return acc;
        },[]);

        if (!data.length) return;

        let comp = {
            modale: componente,
            data: {
                shots: data
            },
            titolo:evento.target.innerText
        };

        this.modal_show(comp);
    }

    shot_selezionato (shot) {
        this.shots_attivi[shot.index] = shot.stato;
    }

    shots_attivi_reset () {
        this.shots_attivi = this.shots_attivi.map(s => false);
    }

    shots_init (shots) {
        this.shots = shots;
        this.shots_attivi = shots.map(s=>false);
    }

    shots_update (evento) {
        this.ShotsService.get('09a6f13f-7f0b-4674-a6e8-49dbecbf58c0',(shots) => {this.shots_init(shots)});
    }

    /**
     * Esegue le richieste del video e degli shot
     */
    ngOnInit() {

        this.VideoService.get('09a6f13f-7f0b-4674-a6e8-49dbecbf58c0', (video) => {this.media = video});
        this.ShotsService.get('09a6f13f-7f0b-4674-a6e8-49dbecbf58c0',(shots) => {
            this.shots_init(shots);
            this.locations = this.ShotsService.annotations().filter(a => a.group === 'location');
        });
    }
}
