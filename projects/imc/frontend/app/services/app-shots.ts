import {Injectable} from '@angular/core';
import {ApiService} from '/rapydo/src/app/api.service';

@Injectable()
export class AppShotsService {

    private _shots = [];

    constructor(private api: ApiService) {
    }

    get (video_id, cb) {

        if (!cb || typeof cb !== 'function') {
            console.log("AppShotService", "Callback mancante");
            return
        }

        this.api.get(
            'videos',
            `${video_id}/shots`
        ).subscribe(
            response => {
                cb(this._shots_process(response.data))
            },
            err => {
                console.log('AppShotService', err)
            }
        )
    }

    shots () {
        return this._shots;
    }

    private _shots_process (shots) {

        let shots_process = [];
        shots.forEach( s => {

            let shot_processato = {
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

            this._annotations_process(shot_processato.annotations, s.annotations);
            this._annotations_sort(shot_processato.annotations);
            shots_process.push(shot_processato);

        });
        this._shots = shots_process;
        return shots_process;

    }

    private _annotations_process (target, annotations) {

        annotations.forEach(a => {

            if (a.attributes.annotation_type.key === 'TAG') {

                a.bodies.forEach(b => {

                    if (b.attributes.spatial !== null && typeof b.attributes.spatial === 'object') {
                        target.locations.push(this._annotation_set(a, b));
                    } else {
                        target.tags.push(this._annotation_set(a, b));
                    }
                })

            } else if (a.attributes.annotation_type.key === 'DSC') {
                target.notes.push(this._annotation_set(a, a.bodies[0]));
            }

            //  todo non so come individuare referenze e links

        })

    }

    private _annotations_sort (target) {
        for (let key in target) {
            if (target[key].length) {
                target[key].sort((a,b) => {
                    if (a.name.toLowerCase() < b.name.toLowerCase()) return -1;
                    if (a.name.toLowerCase() > b.name.toLowerCase()) return 1;
                    return 0;
                })
            }
        }
    }

    private _annotation_set (annotation, annotation_body) {
        return {
            id: annotation.id,
            name: annotation_body.type == 'textualbody' ? annotation_body.attributes.value : annotation_body.attributes.name,
            iri: annotation_body.attributes.iri,
            group: annotation_body.attributes.spatial ? 'location' : 'term',
            creator: annotation.creator.id,
            creator_type: annotation.creator.type
        }
    }
}