import {Component, OnInit, OnDestroy,  Input, Output, EventEmitter} from '@angular/core';
import {AppShotsService, IMC_Annotation} from "../../../services/app-shots";

@Component({
    selector: 'app-media-tags',
    templateUrl: 'app-media-tags.html'
})

export class AppMediaTagsComponent implements OnInit, OnDestroy{

    @Input() shots = null;
    @Output() modale_richiedi: EventEmitter<any> = new EventEmitter();

    constructor(private ShotsService: AppShotsService) {}

    public annotations = {
        elenco: [],
        visualizzate: []
    };

    private _subscription;


    /**
     * Filtra le annotazioni
     * @param evento
     */
    annotations_filter (evento) {
        this.annotations.visualizzate = this.ShotsService.annotations_filter(this.annotations.elenco, evento.target.value);
    }

    /**
     * Richiede apertura modale tag cloud
     */
    all_tags_show () {
        this.modale_richiedi.emit({
            modale: 'tag-cloud',
            titolo: 'Tag cloud',
            data: {
                annotations: this.annotations.elenco,
                shots: this.shots
            }
        });
    }

    /**
     * Richiede apertura modale lista-shot
     * @param evento
     * @param annotation
     */
    annotation_show (evento, annotation) {

        //  filtra gli shot ai quali è assegnata l'annotazione
        let shots = this.shots.filter( s => this.ShotsService.shot_has_annotation(s, annotation));

        this.modale_richiedi.emit({
            modale: 'lista-shots',
            titolo: 'Can also be found in following shots',
            data: {
                annotations: [annotation],
                shots: shots
            },
            classe: 'imc--modal-small'
        });

    }

    annotations_set (shots?) {
        if (shots) {
            this.shots = shots;
        }
        this.annotations.elenco = this.ShotsService.annotations().filter(a => a.type === 'TAG');
        this.annotations.visualizzate = this.annotations.elenco.slice();
    }

    ngOnInit() {
        this.annotations_set();
        this._subscription = this.ShotsService.update.subscribe(shots => {
            this.annotations_set(shots);
        })

    }

    ngOnDestroy () {
        this._subscription.unsubscribe();
    }
}