import {Component, ViewChild , OnInit, OnChanges, OnDestroy, Input} from '@angular/core';
import {AppShotsService, IMC_Annotation} from "../../../../services/app-shots";
import {NgbPopover} from '@ng-bootstrap/ng-bootstrap';

@Component({
    selector: 'app-modal-tag-cloud',
    templateUrl: 'app-modal-tag-cloud.html'
})

export class AppModalTagCloudComponent implements OnInit, OnChanges, OnDestroy {

    @Input() data;
    @Input() media_type: string;

    @ViewChild('p') p;

    constructor(private ShotsService: AppShotsService) {}

    annotations_sorted = {
        count: [],
        alpha: []
    };
    annotations_filtered = {
        count: [],
        alpha: []
    };
    /**
     * Opzioni di ordinamento da visualizzare in interfaccia
     * @type {{key: string; value: string}[]}
     */
    sort_options = [
        {key: 'Popularity', value: 'popularity'},
        {key: 'Alphabetical', value: 'alphabetical'}
    ];

    lista_data = null;

    options = {
        sources: [],
        themes: [],
        sorting: 'popularity'
    };

    _subscription;

    options_set_sorting (event) {
        this.options.sorting = event.target.value;
    }

    shots_show (event, annotation) {

        let shots = this.data.shots.filter( s => this.ShotsService.shot_has_annotation(s, annotation));

        this.lista_data = {
            annotations: [annotation],
            shots: shots
        };

        this.p.open();

    }

    annotations_filter (event) {
        this.annotations_filtered.alpha = this.ShotsService.annotations_filter(this.annotations_sorted.alpha, event.target.value);
        this.annotations_filtered.count = this.ShotsService.annotations_filter(this.annotations_sorted.count, event.target.value);
    }

    ngOnInit() {
        this._subscription = this.ShotsService.update.subscribe(shots => this.data = shots)
    }


    ngOnChanges () {

        this.lista_data = null;

        //  annotazioni ordinate per conteggio
        this.annotations_sorted.count = this.data.annotations.slice();
        this.annotations_sorted.count.sort((a,b) => b.count - a.count);

        //  annotazioni ordinate alfabeticamente
        this.annotations_sorted.alpha = this.data.annotations.slice();
        this.annotations_sorted.alpha.sort((a,b) => {
            if (a.name.toLowerCase() < b.name.toLowerCase()) return -1;
            if (a.name.toLowerCase() > b.name.toLowerCase()) return 1;
            return 0;
        });

        this.annotations_filtered.count = this.annotations_sorted.count.slice();
        this.annotations_filtered.alpha = this.annotations_sorted.alpha.slice();

    }

    ngOnDestroy () {
        this._subscription.unsubscribe();
    }
}