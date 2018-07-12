import { Component, OnInit, OnDestroy, ViewChild, ElementRef, Renderer2, DoCheck } from '@angular/core';
import { Router, Route, ActivatedRoute, Params } from '@angular/router';
import { AppShotsService } from "../../services/app-shots";
import { AppMediaService } from "../../services/app-media";
import { AppModaleComponent } from "../app-modale/app-modale";
import { AppVideoPlayerComponent } from "./app-video-player/app-video-player";
import { AuthService } from "/rapydo/src/app/services/auth";
import { AppVideoService } from "../../services/app-video";
import { AppAnnotationsService } from "../../services/app-annotations";
/**
 * Componente per la visualizzazione del media
 */
@Component({
    selector: 'app-media',
    templateUrl: 'app-media.html'
})

export class AppMediaComponent implements OnInit, OnDestroy {

    //Riferimento alla pagina contenente il media
    // @ViewChild('pageMedia') pageMedia: ElementRef;
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
     * Consente di visualizzare lo strumento per la shot revision
     */
    public shot_revision_is_active: boolean = false;
    private shots_to_restore: any[] = [];
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
        data: {},
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
    //public type_shot: boolean;

    public media_class = '';
    public media_type = '';
    public media_id = '';

    public tab_title = '';

    private _subscription;

    constructor(
        private router: Router,
        private route: ActivatedRoute,
        private AuthService: AuthService,
        private Element: ElementRef,
        private AnnotationService: AppAnnotationsService,
        private MediaService: AppMediaService,
        private ShotsService: AppShotsService,
        private VideoService: AppVideoService) { }

    media_type_set(url) {

        if (url.indexOf('/video') !== -1) {

            this.media_class = 'page-type-video';
            this.media_type = 'video';
            // this.type_shot = true;

        } else if (url.indexOf('/image') !== -1) {

            this.media_class = 'page-type-image';
            this.media_type = 'image';
            // this.type_shot = false;

        }

    }

    start_shot_revision() {
        console.log('Revision mode activated');
        this.shot_revision_is_active = true;
        // create a copy from the actual shot list (DEEP CLONE)
        // this.shots_to_restore = $.extend(true, {}, this.shots);
        this.shots_to_restore = JSON.parse(JSON.stringify(this.shots));
    }

    exit_shot_revision() {
        this.shot_revision_is_active = false;
        // shallow clone is enough here!
        this.shots = this.shots_to_restore.slice(0);
        this.shots_to_restore = [];
    }

    revise_shot($event) {
        console.log('revise shot', $event);
        let op = $event.op;
        switch ($event.op) {
            case "join":
                this.join_shots($event.index, $event.index + 1);
                break;
            default:
                console.warn('Invalid operation in revising shot for ' + $event.op);
        }
    }

    private join_shots(idxA, idxB) {
        let shotA = this.shots[idxA];
        let shotB = this.shots[idxB];
        shotA.attributes.duration += shotB.attributes.duration;
        shotA.attributes.end_frame_idx = shotB.attributes.end_frame_idx;
        Object.keys(shotA.annotations).forEach(e => {
            // merge annotations
            shotA.annotations[e].push(...shotB.annotations[e]);
        });
        this.shots[idxA] = shotA;
        // remove shotB from the list
        /*console.log('remove shot idx', idxB);*/
        this.shots.splice(idxB, 1);
        // update the subsequent shot numbers
        for (let i = idxA + 1; i < this.shots.length; i++) {
            this.shots[i].attributes.shot_num = this.shots[i].attributes.shot_num - 1;
        }
    }

    private split_shot(shot) {

    }

    save_revised_shots() {
        console.log('save revised shots');
        this.shot_revision_is_active = false;
        // because the shot list size could have changed then update the list of 'shot_attivi'
        this.shots_attivi = this.shots.map(s => false);
    }


    /**
     * Modifica la visibilità dello strumento per la shot revision
     */
    shot_revision_toggle() {
        this.shot_revision_is_active = !this.shot_revision_is_active;
    }


    /**
     * Modifica la visibilità dello strumento per la selezione multipla degli shot
     * e ne resetta lo stato deselezionando tutti
     */
    multi_annotations_toggle() {
        this.multi_annotations_is_active = !this.multi_annotations_is_active;
        this.shots_attivi_reset();
    }

    /**
     * Apre una modale visualizzando al suo interno il compontente coi dati ricevuti
     * @param componente Configurazione del componente daq visualizzare nella modale
     */
    modal_show(componente) {

        //  fermo il video principale
        if (this.appVideo) {
            this.appVideo.video.pause();
        }
        this.modale.type = componente.modale;
        if (componente.next) {
            // use the next flag to add the next shot to the list
            let next_shot_num = componente.data.shots.slice(-1)[0].attributes.shot_num + 1;
            componente.data.shots.push(this.shots[next_shot_num]);
        }
        this.modale.data = componente.data;

        this.appModale.open(componente.titolo, this.MediaService.type(), componente.classe);
    }

    /**
     * Apre una modale visualizzando al suo interno il componente coi dati ricevuti
     * Inserisce nei dati da visualizzare gli shots selezionati
     * @param evento Evento richiamante
     * @param componente Componente selezionato
     */
    modal_show_multi(evento, componente) {

        let data = this.shots_attivi.reduce((acc, value, index) => {
            if (value) {
                acc.push(this.shots[index])
            }
            return acc;
        }, []);

        if (!data.length) return;

        let comp = {
            modale: componente,
            data: {
                shots: data
            },
            titolo: evento.target.innerText
        };

        this.modal_show(comp);
    }

    shot_selezionato(evento) {
        this.shots_attivi[evento.index] = evento.stato;
    }

    shots_attivi_reset() {
        this.shots_attivi = this.shots_attivi.map(s => false);
    }

    shots_init(shots) {
        //  Questo tipo di aggiornamento serve per non ridisegnare tutti i componenti collegati agli shots
        if (this.shots.length) {
            this.shots.forEach((s, idx) => {
                s.annotations = shots[idx].annotations;
            })
        } else {
            this.shots = shots;
        }
        this.shots_attivi = shots.map(s => false);
    }

    shots_update(evento) {
        if (this.media_type === 'video') {
            this.ShotsService.get();
        } else if (this.media_type === 'image') {
            this.AnnotationService.get(this.media_id, 'images');
        }
    }

    video_player_set(event) {
        this.VideoService.video_set(event);
    }

    /* Seleziona il titolo per le tabs degli shot */
    tab_title_set(evento) {

        let target = evento.target;

        if (target.nodeName.toUpperCase() === 'LI') {
            target = target.querySelector('a > i');
        } else if (target.nodeName.toUpperCase() === 'A') {
            target = target.querySelector('i');
        }
        this.tab_title = target.attributes.getNamedItem('data-title').value;
    }

    media_entity_normalize(mediaEntity) {

        //  Normalizzo i dati delle immagini
        if (this.media_type === 'image') {

            // anno di produzione
            if (mediaEntity.attributes.date_created) {
                mediaEntity.attributes.production_years = mediaEntity.attributes.date_created;
            }

            // titolo principale
            if (mediaEntity.relationships.titles.length) {
                mediaEntity.attributes.identifying_title = mediaEntity.relationships.titles[0].attributes.text;
            }

            this.locations = [];

        }

        //  elimino i titoli aggiuntivi se sono identici a quello identificativo
        if (mediaEntity.relationships.titles.length) {
            mediaEntity.relationships.titles = mediaEntity.relationships.titles.filter(t => t.attributes.text !== mediaEntity.attributes.identifying_title)
        }

        return mediaEntity;
    }

    /**
     * Esegue le richieste del video e degli shot
     */
    ngOnInit() {

        this.user = this.AuthService.getUser();
        this.media_type_set(this.router.url);

        this._subscription = this.route.params.subscribe((params: Params) => {

            this.media_id = params['uuid'];
            let endpoint = (this.router.url.indexOf("videos") != -1) ? 'videos' : 'images';

            this.MediaService.get(this.media_id, endpoint, (mediaEntity) => {

                this.media = this.media_entity_normalize(mediaEntity);

                // To be confirmed
                setTimeout(() => {
                    this.Element.nativeElement.querySelector('#pills-tab > li').click();
                }, 100);

                if (this.media_type === 'video') {
                    this.ShotsService.get(this.media_id, endpoint);
                }

                if (this.media_type === 'image') {
                    this.AnnotationService.get(this.media_id, endpoint);
                    const annotations_subscription = this.AnnotationService.update.subscribe(annotations => {
                        this.ShotsService.get(this.media_id, endpoint, {
                            annotations: annotations,
                            links: this.media.links,
                            item_id: this.media.relationships.item[0].id
                        });
                    });
                    this._subscription.add(annotations_subscription);
                }

                const shots_subscription = this.ShotsService.update.subscribe(shots => {
                    this.shots_init(shots);
                    const annotations = this.ShotsService.annotations();
                    this.annotations_count = annotations.length;
                    this.locations = annotations.filter(a => a.group === 'location');
                });
                this._subscription.add(shots_subscription);


            });


        });

    }

    ngOnDestroy() {
        this._subscription.unsubscribe();
    }

}
