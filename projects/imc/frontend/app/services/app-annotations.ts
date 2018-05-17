import {Injectable} from '@angular/core';
import {ApiService} from '/rapydo/src/app/services/api';

@Injectable()
export class AppAnnotationsService {

    constructor(private api: ApiService) {}

    create_tag (shots_ids, sources, cb) {
        console.log("sources",  sources);
        let d = sources.map(s => {
            if (s.iri) {
                return AppAnnotationsService.resource_body(s)
            } else {
                return AppAnnotationsService.textual_body_term(s)
            }
        })
        console.log("sources => data",  d);
        let data = {
            motivation: 'tagging',
            body: sources.map(s => {
                if (s.iri) {
                    return AppAnnotationsService.resource_body(s)
                } else {
                    return AppAnnotationsService.textual_body_term(s)
                }
            })
        };

        this.create( shots_ids, data, cb);
    }


    create_note (shots_ids, note, cb) {

        let data = {
            motivation: 'describing',
            body: AppAnnotationsService.textual_body(note),
            private: note.private
        };

        this.create( shots_ids, data, cb);

    }

    create (shots_ids, data, cb) {

        data = Object.assign(data, {target:`shot:${shots_ids}`});

        this.api.post(
            'annotations',
            data
        ).subscribe(
            response => {
                cb(response)
            },
            err => {
                console.log("err",  err);
            }
        )
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