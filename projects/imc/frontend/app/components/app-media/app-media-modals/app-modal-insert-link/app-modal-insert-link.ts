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
    //links_all: IMC_Annotation[] = [];
    links_all: any[] = [];

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
                        // FIXME
                    }
                    let anno = {
                        name: l.value,
                        private: l.private,
                        type: "LNK"
                    }
                    console.log(anno);
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
        console.log(this.links_all);
        this.add_link_info.hide();
        this.link.url = '';
    }
}