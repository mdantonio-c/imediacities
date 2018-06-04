import {Component, OnInit, ViewChild, ElementRef, DoCheck} from '@angular/core';
import {ActivatedRoute, Router, Params} from '@angular/router';
import {AppShotsService} from "../../services/app-shots";
import {AppMediaService} from "../../services/app-media";
import {AppModaleComponent} from "../app-modale/app-modale";
import {AppVideoPlayerComponent} from "./app-video-player/app-video-player";
import {AuthService} from "/rapydo/src/app/services/auth";
import {AppVideoService} from "../../services/app-video";

/**
 * Componente per la visualizzazione del media
 */
@Component({
    selector: 'app-media',
    templateUrl: 'app-media.html'
})

export class AppMediaComponent implements OnInit {

    //Riferimento alla pagina contenente il media
    @ViewChild('pageMedia') pageMedia: ElementRef;
    /**
     * Riferimento al componente AppModale
     */
    @ViewChild('appModale') appModale: AppModaleComponent;
    /**
     * Riferimento al componente AppVideoPlayer
     */
    @ViewChild('appVideo') appVideo: AppVideoPlayerComponent;
    /**
     * Conteggio annotazioni
     * @type {number}
     */
    public annotations_count = 0;
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
    /**
     * Elenco delle location da passare alla mappa
     */
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
    public user = {};
    public title_shot: string;
    public type_shot: boolean;

    constructor(
        private AuthService: AuthService,
        private route: ActivatedRoute,
        private router: Router,
        private MediaService: AppMediaService,
        private ShotsService: AppShotsService,
        private VideoService: AppVideoService ) {


    }

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

        this.appModale.open(componente.titolo, this.MediaService.type(), componente.classe);

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

    shot_selezionato (evento) {
        this.shots_attivi[evento.index] = evento.stato;
    }

    shots_attivi_reset () {
        this.shots_attivi = this.shots_attivi.map(s => false);
    }

    shots_init (shots) {
        //  Questo tipo di aggiornamento serve per non ridisegnare tutti i componenti collegati agli shots
        if (this.shots.length) {
            this.shots.forEach((s,idx) => {
                s.annotations = shots[idx].annotations;
            })
        } else {
            this.shots = shots;
        }
        this.shots_attivi = shots.map(s=>false);
    }

    shots_update (evento) {
        this.ShotsService.get();
    }

    video_player_set (event) {
        this.VideoService.video_set(event);
    }

    /* Seleziona il titolo per le tabs degli shot */
    titleTabShot(title) {
        this.title_shot = title;
    }
    // Controllo della classe page-type-video o page-type-media all'interno del div principale che contiene il media
    ngAfterViewInit() {
        setTimeout(() => {
            if (this.pageMedia.nativeElement.classList.contains('page-type-video')) {
                this.type_shot = true;
                /* Settaggio del titolo iniziale delle tab-shot */
                this.title_shot = 'shots';
            } else if (this.pageMedia.nativeElement.classList.contains('page-type-image')) {
                this.type_shot = false;
                this.title_shot = 'picture';
            }
        }, 1000);
    }

    /**
     * Esegue le richieste del video e degli shot
     */
    ngOnInit() {
        this.user = this.AuthService.getUser();

        this.route.params.subscribe((params: Params) => {
            let mediaID = params['uuid'];
            let endpoint = (this.router.url.indexOf("videos") != -1) ? 'videos' : 'images';
            this.MediaService.get(mediaID, endpoint, (mediaEntity) => {
                this.media = mediaEntity;
                if (this.media.type === 'aventity') {
                    this.ShotsService.get(mediaID);
                    this.ShotsService.update.subscribe(shots => {
                        this.shots_init(shots);
                        const annotations = this.ShotsService.annotations();
                        this.annotations_count = annotations.length;
                        this.locations = annotations.filter(a => a.group === 'location')
                    })
                }
            });
        });
    }

}
