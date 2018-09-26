import { Component, OnChanges, Input, Output, EventEmitter, ViewChild } from '@angular/core';
import { AppMediaModal } from "../app-media-modal";
import { AppAnnotationsService } from "../../../../services/app-annotations";
import { IMC_Annotation } from "../../../../services/app-shots";
import { infoResult } from "../../../../decorators/app-info";

@Component({
    selector: 'app-modal-insert-link',
    templateUrl: 'app-modal-insert-link.html'
})
export class AppModalInsertLinkComponent implements OnChanges {

    @Input() data;
    @Input() media_type: string;

    @Output() shots_update: EventEmitter<any> = new EventEmitter();
    @infoResult() add_link_info;
    @infoResult() save_result;

    options = true;
    optionsCheckbox = [
        { label: 'Video', checked: true },
        { label: 'Photo', checked: true },
        { label: 'Reference', checked: false },
        { label: 'Note', checked: false }
    ];
    link = {
        url: '',
        private: false
    };
    links_all: IMC_Annotation[] = [];

    @ViewChild(AppMediaModal) modal: AppMediaModal;

    constructor(private AnnotationsService: AppAnnotationsService) {
    }

    /**
     * Adds the link to the list of terms to be saved.
     */
    addLink() {
        let exists = this.links_all.some(e => {
            // if site has an end slash (like: www.example.com/),
            // then remove it and return the site without the end slash
            return this.link.url.trim().replace(/\/$/, '') === e.name.replace(/\/$/, '');
        });
        if (exists) {
            this.add_link_info.show('error', 'This link has already been added');
        } else {
            this.add_link_info.hide();
            let l = {
                private: this.link.private,
                value: this.link.url.trim()
            };
            this.AnnotationsService.create_link(
                this.data.shots.map(s => s.id),
                l,
                this.media_type,
                (err, r) => {

                    if (err) {
                        this.save_result.show('error');
                        return;
                    }
                    let resp = r[0].data;
                    let anno: IMC_Annotation = {
                        creation_date: resp.attributes.creation_datetime,
                        creator: resp.creator ? resp.creator.id : null,
                        creator_type: resp.creator ? resp.creator.type : null,
                        embargo: resp.embargo || null,
                        group: null,
                        body_id: resp.bodies[0].id,
                        id: resp.id,
                        iri: null,
                        name: resp.bodies[0].attributes.value,
                        private: resp.attributes.private,
                        spatial: null,
                        type: resp.attributes.annotation_type.key,
                        source: resp.source.attributes.item_type.key,
                        source_uuid: resp.source.id
                    }
                    this.links_all.push(anno);
                    this.save_result.show('success', 'Link added successfully');
                    this.shots_update.emit(r);
                }
            );
        }
        this.link.url = '';
    }

    ok() {
        this.modal.chiudi();
    }

    ngOnChanges() {
        this.links_all = this.AnnotationsService.merge(this.data.shots, 'links');
        this.add_link_info.hide();
        this.link.url = '';
    }
}