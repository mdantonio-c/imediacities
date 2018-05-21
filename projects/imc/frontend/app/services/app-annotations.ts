import {Injectable} from '@angular/core';
import {ApiService} from '/rapydo/src/app/services/api';
import {Observable} from 'rxjs/Observable';
import 'rxjs/add/observable/forkJoin';

@Injectable()
export class AppAnnotationsService {

    constructor(private api: ApiService) {}

    create_tag (shots_ids, sources, cb) {

        let  observables:Observable<any>[] = [];
        shots_ids.forEach(shot_id => observables.push(
            this.api.post(
                'annotations',
                {
                    target:`shot:${shot_id}`,
                    motivation: 'tagging',
                    body: sources.map(s => {
                        if (s.iri) {
                            return AppAnnotationsService.resource_body(s)
                        } else {
                            return AppAnnotationsService.textual_body_term(s)
                        }
                    })
                }
            ).map((res)=>res))
        );

        Observable.forkJoin(
            observables
        ).subscribe(res => cb(res));


    }

    create_note (shots_ids, note, cb) {

        let  observables:Observable<any>[] = [];
        shots_ids.forEach(shot_id => observables.push(
            this.api.post(
                'annotations',
                {
                    target:`shot:${shot_id}`,
                    motivation: 'describing',
                    body: AppAnnotationsService.textual_body(note),
                    private: note.private
                }
            ).map((res)=>res))
        );

        Observable.forkJoin(
            observables
        ).subscribe(res => cb(res));

    }

    delete_tag (annotation) {
        // this.api.delete(
        //     'annotations',
        //     annotation.id
        // ).subscribe(
        //     response => {
        //         console.log("delete annotation response",  response);
        //     },
        //     err => {
        //         console.log("delete annotation err",  err);
        //     }
        // );
        console.log("todo delete",  annotation);
    }

    merge (shots, gruppo) {

        let mappa = new Map();
        shots.forEach(s => {
            s.annotations[gruppo].forEach(t => mappa.set(t.id, t))
        });

        return Array.from(mappa).map(t => t[1]).sort((a, b) => {
            if (a.name.toLowerCase() < b.name.toLowerCase()) return -1;
            if (a.name.toLowerCase() > b.name.toLowerCase()) return 1;
            return 0;
        });

    }

    static source (s) {
        return {
            iri: s.iri,
            name: s.name
        }
    }

    static spatial (s) {
        if (s.lat && s.long) {
            return {
                lat: s.lat,
                long: s.long
            }
        } else {
            return null;
        }
    }

    static textual_body (note) {
        return {
            type: 'TextualBody',
            value: note.value,
            language: note.language
        }
    }

    static textual_body_term (term) {
        return {
            type: 'TextualBody',
            value: term.value || term.name,
            purpose: 'tagging'
        }
    }

    static resource_body (source) {
        const spatial = AppAnnotationsService.spatial(source);
        const s = {
            type: 'ResourceBody',
            purpose: 'tagging',
            source: AppAnnotationsService.source(source),
        };
        if (spatial) {
            s['spatial'] = spatial;
        }
        return s;
    }

}