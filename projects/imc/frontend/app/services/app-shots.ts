import {Injectable, Output, EventEmitter} from '@angular/core';
import {ApiService} from '/rapydo/src/app/services/api';

@Injectable()
export class AppShotsService {

    private _annotations_all: IMC_Annotation[] = [];
    private _annotations_map = new Map();
    private _media_id = '';
    private _shots: IMC_Shot[] = [];

    @Output() update: EventEmitter<any> = new EventEmitter();
    private _others_data_as_object;

    constructor(private api: ApiService) {
    }

    /**
     * Ottiene gli shots del video media_id
     * @param media_id
     * @param endpoint
     * @param others_data_as_object
     */
    get (media_id?, endpoint?, others_data_as_object?) {

        if (!media_id) {
            media_id = this._media_id;
        }

        //  Quando l'applicazione non è di tipo video non chiamo shots, ma li simulo.
        if (endpoint && endpoint !== 'videos') {

            const shot_mimic = [
                {
                    id: others_data_as_object.item_id,
                    links: others_data_as_object.links,
                    attributes: {
                        shot_num:0
                    },
                    annotations: others_data_as_object.annotations
                }
            ];

            this._media_id = media_id;
            this._shots_parse(shot_mimic, 'image');
            this.update.emit(this._shots);
            return;
        }

        this.api.get(
            endpoint || 'videos',
            `${media_id}/shots`
        ).subscribe(
            response => {
                this._media_id = media_id;
                this._shots_parse(response.data, 'video');
                this.update.emit(this._shots);
            },
            err => {
                console.log('AppShotService', err)
            }
        )
    }
    media_id () {
        return this._media_id;
    }
    /**
     * Ritorna gli shots processati
     * @returns {IMC_Shot[]}
     */
    shots (): IMC_Shot[] {
        return this._shots;
    }
    /**
     * Verifica se l'annotazione annotation esiste nello shot shot
     * @param shot
     * @param annotation
     * @returns {boolean}
     */
    shot_has_annotation (shot, annotation) {

        let found = 0;
        for (let key in shot.annotations) {
            if (shot.annotations[key].length) {
                found += shot.annotations[key].filter(s =>  s.id === annotation.id ).length;
            }
        }
        return found > 0;
    }
    /**
     * Ritorna un oggetto con tutte le annotazioni ordinate alfabeticamente
     * @returns {IMC_Annotation[]}
     */
    annotations (): IMC_Annotation[] {
        return this._annotations_all;
    }

    /**
     * Filtra le annotazioni in base al filtro passato
     * @param array_da_filtrare
     * @param filtro
     * @param {string} proprieta - proprietà di annotation su cui testare il filtro
     * @param {string} re_flags
     * @returns {IMC_Annotation[]}
     */
    annotations_filter (array_da_filtrare, filtro, proprieta = 'name', re_flags = 'i'): IMC_Annotation[] {

        if (!array_da_filtrare) {
            array_da_filtrare = this._annotations_all.slice();
        }

        filtro = new RegExp( filtro, re_flags );
        return array_da_filtrare.filter(annotation => filtro.test(annotation[proprieta]))

    }
    /**
     * Processa gli shot
     * ne estrae proprietà e annotazioni
     * ritornando l'elenco degli shot elaborato
     * @param shots
     * @param media_type
     * @returns {IMC_Shot[]}
     * @private
     */
    private _shots_parse (shots, media_type): IMC_Shot[] {

        let shots_processed = [];
        //  per ogni shot
        shots.forEach( (s, index) => {

            let shot_processato: IMC_Shot = {
                id: s.id,
                attributes: s.attributes,
                links: s.links,
                annotations: {
                    locations: [],
                    tags: [],
                    notes: [],
                    references: [],
                    links: []
                }
            };
            //  processo annotazioni
            this._annotations_parse(shot_processato.annotations, s.annotations, media_type, index);
            AppShotsService._annotations_sort(shot_processato.annotations);
            shots_processed.push(shot_processato);

        });
        this._shots = shots_processed;
        this._annotations_all_from_map();
        return this.shots();

    }
    /**
     * Processa le annotazioni suddividendole per categoria
     * @param target
     * @param annotations
     * @param media_type
     * @param shot_indice shot in cui compare l'annotazione
     * @private
     */
    private _annotations_parse (target, annotations, media_type, shot_indice) {

        annotations.forEach(annotation => {

            //  Term tag e locations
            if (annotation.attributes.annotation_type.key === 'TAG') {

                annotation.bodies.forEach(body => {
                    let tipo = 'tags';

                    if (body.attributes.spatial !== null && typeof body.attributes.spatial === 'object') {
                        tipo = 'locations';
                    }

                    this._annotation_add(target[tipo], this._annotation_set(annotation, body, media_type), shot_indice)
                })

                //  Note
            } else if (annotation.attributes.annotation_type.key === 'DSC') {
                this._annotation_add(target.notes, this._annotation_set(annotation, annotation.bodies[0], media_type), shot_indice)
            }

            //  todo non so come individuare referenze e links

        })

    }
    /**
     * Aggiunge l'annotazione annotation all'array target
     * e aggiunge l'annotazione all'elenco generale gestendone il conteggio e l'elenco degli shot in cui appare
     * @param target
     * @param annotation
     * @param shot_indice Shot in cui compare l'annotazione
     * @private
     */
    private _annotation_add (target, annotation, shot_indice) {

        annotation.shots_idx = [shot_indice];
        target.push(annotation);

        if (this._annotations_map.has(annotation.id)) {
            let annotation_from_map = this._annotations_map.get(annotation.id);
            annotation_from_map.count += 1;
            annotation_from_map.shots_idx.push(shot_indice);
        } else {
            annotation.count = 1;
            annotation.shots_idx = [shot_indice];
            this._annotations_map.set(annotation.id, annotation);
        }

    }
    private _annotations_all_from_map () {
        this._annotations_all = Array.from(this._annotations_map).map(annotation => annotation[1]);
        this._annotations_all.sort(AppShotsService._sort_alpha);
        this._annotations_map.clear();
    }
    /**
     * Crea un'annotazione riorganizzando i dati
     * @param annotation
     * @param annotation_body
     * @param media_type
     * @returns {IMC_Annotation}
     * @private
     */
    private _annotation_set (annotation, annotation_body, media_type): IMC_Annotation {

        return {
            creation_date: annotation.attributes.creation_datetime,
            creator: annotation.creator.id,
            creator_type: annotation.creator.type,
            embargo: annotation.embargo || null,
            group: annotation_body.attributes.spatial ? 'location' : 'term',
            body_id: annotation_body.id,
            id: annotation.id,
            iri: annotation_body.attributes.iri || null,
            name: annotation_body.type == 'textualbody' ? annotation_body.attributes.value : annotation_body.attributes.name,
            private: annotation.private || false,
            spatial: annotation_body.attributes.spatial || null,
            type: annotation.attributes.annotation_type.key,
            source: media_type,
            source_uuid: this._media_id
        };
    }

    /**
     * Ordina alfabeticamente le annotazioni
     * @param target
     * @private
     */
    static _annotations_sort (target) {
        for (let key in target) {
            if (target.hasOwnProperty(key) && target[key].length) {
                target[key].sort(AppShotsService._sort_alpha)
            }
        }
    }

    /**
     * Ordinamento alfabetico
     * @param a
     * @param b
     * @returns {number}
     * @private
     */
    static _sort_alpha (a, b) {
        if (a.name.toLowerCase() < b.name.toLowerCase()) return -1;
        if (a.name.toLowerCase() > b.name.toLowerCase()) return 1;
        return 0;
    }


}

export interface IMC_Annotation {
    creation_date: Date,
    creator: string,
    creator_type: string,
    embargo: Date,
    group: string,
    body_id: string,
    id: string,
    iri: string,
    name: string,
    private: boolean,
    spatial: number[],
    type: string,
    source: string,
    source_uuid: string
}

export interface IMC_Shot {
    id: string,
    attributes: {},
    links: {},
    annotations: {
        locations: IMC_Annotation[],
        tags: IMC_Annotation[],
        notes: IMC_Annotation[],
        references: IMC_Annotation[],
        links: IMC_Annotation[]
    }
}
