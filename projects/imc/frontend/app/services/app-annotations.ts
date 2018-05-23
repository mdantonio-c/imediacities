import {Injectable} from '@angular/core';
import {ApiService} from '/rapydo/src/app/services/api';
import {Observable} from 'rxjs/Observable';
import 'rxjs/add/observable/forkJoin';
import {AppShotsService} from "./app-shots";

@Injectable()
export class AppAnnotationsService {

    constructor(private api: ApiService, private ShotsService: AppShotsService) {}

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

    delete_request (annotation) {
        let confirm = window.confirm('Delete the annotation "' + annotation.name + '"?');
        if (confirm) {
            this.delete_tag(annotation);
        }
    }

    delete_tag (annotation) {

        const bodyRef = annotation.iri ? `resource:${annotation.iri}` : `textual:${annotation.name}`;

        this.api.delete(
            'annotations',
            `${annotation.id}?body_ref=${encodeURIComponent(bodyRef)}`
        ).subscribe(
            response => {
                this.ShotsService.get();
            },
            err => {
            }
        );

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
        if (s.lat && s.lng) {
            return {
                lat: s.lat,
                long: s.lng
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