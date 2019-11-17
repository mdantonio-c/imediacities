import { Component, OnChanges, Input, Output, EventEmitter, ViewChild } from '@angular/core';
import { AppMediaModal } from "../app-media-modal";
import { AppAnnotationsService } from "../../../../services/app-annotations";
import { IMC_Annotation } from "../../../../services/app-shots";
import { infoResult } from "../../../../decorators/app-info";
import { AuthService } from "@rapydo/services/auth";
import { is_annotation_owner } from "../../../../decorators/app-annotation-owner";

const url_protocol = /^https?:\/\//i;

@Component({
    selector: 'app-modal-insert-link',
    templateUrl: 'app-modal-insert-link.html'
})
export class AppModalInsertLinkComponent implements OnChanges {

    @Input() data;
    @Input() media_type: string;
    @is_annotation_owner() is_annotation_owner;

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
    private _current_user;

    @ViewChild(AppMediaModal, { static: false }) modal: AppMediaModal;

    constructor(
        private AnnotationsService: AppAnnotationsService,
        private AuthService: AuthService) {
    }

    /**
     * Adds the link to the list of terms to be saved.
     */
    addLink() {
        let linkURL = this.link.url.trim();
        let valid = true;
        let errorMsg = '';
        // check for valid URL
        if (valid && !this.isValidURL(linkURL)) {
            errorMsg = 'This link is not valid';
            if (!url_protocol.test(linkURL)) { errorMsg += '. Missing protocol?'; }
            valid = false;
        }
        // check for existing link
        if (valid && this.links_all.some(e => {
            // if site has an end slash (like: www.example.com/),
            // then remove it and return the site without the end slash
            return linkURL.replace(/\/$/, '') === e.name.replace(/\/$/, '');
        })) {
            errorMsg = 'This link has already been added';
            valid = false;
        }
        if (!valid) {
            this.add_link_info.show('error', errorMsg);
        } else {
            this.add_link_info.hide();
            let l = {
                private: this.link.private,
                value: linkURL
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
                        language: null,
                        spatial: null,
                        type: resp.attributes.annotation_type.key,
                        source: resp.source.attributes.item_type.key,
                        source_uuid: resp.source.id
                    }
                    this.links_all.push(anno);
                    this.save_result.show('success', 'Link added successfully');
                    this.shots_update.emit(r);
                    this.link.url = '';
                }
            );
        }
    }

    removeLink(link: IMC_Annotation) {
        /*if (!this.can_delete) return;*/
        if (link.id) {
            this.AnnotationsService.delete_tag(link, link.source);
            this.links_all = this.links_all.filter(anno => anno.id !== link.id);
        }
    }

    canRemoveLink(link: IMC_Annotation) {
        return this.is_annotation_owner(this._current_user, link.creator);
    }

    ok() {
        this.modal.chiudi();
    }

    ngOnInit() {
        this._current_user = this.AuthService.getUser();
    }

    ngOnChanges() {
        this.links_all = this.AnnotationsService.merge(this.data.shots, 'links');
        this.add_link_info.hide();
        this.link.url = '';
    }

    private isValidURL(str) {
        var pattern = new RegExp('^https?:\\/\\/' + // protocol
            '(?:\\S+(?::\\S*)?@)?' + // authentication
            '((([a-z\\d]([a-z\\d-]*[a-z\\d])*)\\.)+[a-z]{2,}|' + // domain name
            '((\\d{1,3}\\.){3}\\d{1,3}))' + // OR ip (v4) address
            /*'(\\:\\d+)?(\\/[-a-z\\d%_.~+]*)*' + // port and path
            '(\\?[;&a-z\\d%_.~+=-]*)?' + // query string
            '(\\#[-a-z\\d_]*)?$' + // fragment locater*/
            '', 'i');
        if (!pattern.test(str)) {
            return false;
        } else {
            return true;
        }
    }

}