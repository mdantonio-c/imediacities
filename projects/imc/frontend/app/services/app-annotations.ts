import { Injectable, Output, EventEmitter } from '@angular/core';
import { ApiService } from '/rapydo/src/app/services/api';
import { NotificationService } from '/rapydo/src/app/services/notification';
import { Observable } from 'rxjs/';
import 'rxjs/add/observable/forkJoin';
import { AppShotsService } from "./app-shots";

@Injectable()
export class AppAnnotationsService {

    _annotations = [];

    private confirmationPopover_config = {
        popoverTitle: 'Delete',
        popoverMessage: 'This operation cannot be undone<br>Do you wish to continue?',
        appendToBody: true
    };

    @Output() update: EventEmitter<any> = new EventEmitter();

    constructor(
        private api: ApiService,
        private ShotsService: AppShotsService,
        private notify: NotificationService
        ) { }

    create_tag(shots_ids, sources, media_type, cb) {
        let observables: Observable<any>[] = [];
        shots_ids.forEach(shot_id => observables.push(
            this.api.post(
                'annotations',
                {
                    target: media_type === 'video' ? `shot:${shot_id}` : `item:${shot_id}`,
                    motivation: 'tagging',
                    body: sources.map(s => {
                        if (s.iri) {
                            return AppAnnotationsService.resource_body(s)
                        } else {
                            return AppAnnotationsService.textual_body_term(s)
                        }
                    })
                }
            ).map((res) => res))
        );

        Observable.forkJoin(
            observables
        ).subscribe(
            res => cb(null, res),
            err => cb(err, null)
        );
    }

    create_note(shots_ids, note, media_type, cb) {
        let observables: Observable<any>[] = [];
        shots_ids.forEach(shot_id => observables.push(
            this.api.post(
                'annotations',
                {
                    // target:`shot:${shot_id}`,
                    target: media_type === 'video' ? `shot:${shot_id}` : `item:${shot_id}`,
                    motivation: 'describing',
                    body: AppAnnotationsService.textual_body(note),
                    private: note.private
                }
            ).map((res) => res))
        );

        Observable.forkJoin(
            observables
        ).subscribe(res => cb(res));
    }
    create_link(shots_ids, link, media_type, cb) {

        let observables: Observable<any>[] = [];
        shots_ids.forEach(shot_id => observables.push(
            this.api.post(
                'annotations',
                {
                    target: media_type === 'video' ? `shot:${shot_id}` : `item:${shot_id}`,
                    motivation: 'linking',
                    body: AppAnnotationsService.textual_body(link),
                    private: link.private
                }
            ).map((res) => res))
        );
        
        Observable.forkJoin(
            observables
        ).subscribe(
            res => cb(null, res),
            err => cb(err, null));
    }

    create_reference(shots_ids, reference, media_type, cb) {

        let observables: Observable<any>[] = [];
        shots_ids.forEach(shot_id => observables.push(
            this.api.post(
                'annotations',
                {
                    target: media_type === 'video' ? `shot:${shot_id}` : `item:${shot_id}`,
                    motivation: 'linking',
                    body: AppAnnotationsService.bibliographic_reference(reference),
                    private: reference.private
                }
            ).map((res) => res))
        );
        
        Observable.forkJoin(
            observables
        ).subscribe(
            res => cb(null, res),
            err => cb(err, null));
    }

    delete_request(annotation, media_type) {
        let confirm = window.confirm('Delete the annotation "' + annotation.name + '"?');
        if (confirm) {
            this.delete_tag(annotation, media_type);
        }
    }

    delete_tag(annotation, media_type) {
        const bodyRef = annotation.iri ? `resource:${annotation.iri}` : `textual:${annotation.name}`;
        this.api.delete(
            'annotations',
            `${annotation.id}?body_ref=${encodeURIComponent(bodyRef)}`
        ).subscribe(
            response => {
                /*console.log("media_type", media_type);*/
                if (media_type === 'video') {
                    this.ShotsService.get();
                } else if (media_type === 'image') {
                    this.get(annotation.source_uuid, 'images');
                }
            },
            err => { }
        );
    }
    update_note_private(note, new_private) {
        this.api.put(
            'annotations',
            `${note.id}`,
                {
                    body: AppAnnotationsService.textual_body_2(note),
                    private: new_private
                }
        ).subscribe(
            response => {
                //console.log("Updated note: ", response.data);
                note.private = response.data.attributes.private;
            },
            err => {
                console.error("Error updating note: err=", err);
                this.notify.showError('The update of the note is failed');
            }
        );
    }
    delete_anno(annotation, media_type) {
        this.api.delete(
            'annotations',
            `${annotation.id}`
        ).subscribe(
            response => {
                console.log("media_type", media_type);
                if (media_type === 'video') {
                    this.ShotsService.get();
                } else if (media_type === 'image') {
                    this.get(annotation.source_uuid, 'images');
                }
            },
            err => {
                console.error("Error deleting annotation " + annotation.id);
            }
        );
    }

    get(media_id, endpoint) {

        this.api.get(
            endpoint,
            `${media_id}/annotations`
        ).subscribe(
            response => {
                this._annotations = response.data;
                this.update.emit(this._annotations);
            },
            err => {
                console.log("err", err);
            }
        )
    }

    merge(shots, gruppo) {
        let mappa = new Map();

        shots.forEach(s => {
            s.annotations[gruppo].forEach(t => mappa.set(t.id + '_' + t.body_id, t))
        });

        return Array.from(mappa).map(t => t[1]).sort((a, b) => {
            if (a.name.toLowerCase() < b.name.toLowerCase()) return -1;
            if (a.name.toLowerCase() > b.name.toLowerCase()) return 1;
            return 0;
        });

    }

    popover() {
        let popover_conf = Object.assign({}, this.confirmationPopover_config);
        return popover_conf;
    }

    static source(s) {
        return {
            iri: s.iri,
            name: s.name
        }
    }

    static spatial(s) {
        if (s.lat && s.lng) {
            return {
                lat: s.lat,
                long: s.lng
            }
        } else {
            return null;
        }
    }

    static _encode_language (lang): string {
        let language;
        switch (lang){
            case 'Català':
                language='ca';
                break;
            case 'Dansk':
                language='da';
                break;
            case 'Deutsche':
                language='de';
                break;
            case 'English':
                language='en';
                break;
            case 'Español':
                language='es';
                break;
            case 'Français':
                language='fr';
                break;
            case 'Italiano':
                language='it';
                break;
            case 'Nederlands':
                language='nl';
                break;
            case 'Svenska':
                language='sv';
                break;
            case 'Ελληνικά':
                language='el';
                break;
            default:
                language='';
                break;
        }

        return language;
    }
    // I had to create the textual_body_2
    //  because I need it to update notes
    static textual_body_2(note) {
        return {
            type: 'TextualBody',
            value: note.name,
            language: this._encode_language(note.language)
        }
    }
    static textual_body(note) {
        return {
            type: 'TextualBody',
            value: note.value,
            language: note.language
        }
    }
    static textual_body_term(term) {
        return {
            type: 'TextualBody',
            value: term.value || term.name,
            purpose: 'tagging'
        }
    }

    static resource_body(source) {
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

    static bibliographic_reference(reference) {
        return {
            type: "BibliographicReference",
            value: reference 
        };
    }

}