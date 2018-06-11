import {Component, HostBinding, Input, OnInit} from '@angular/core';

@Component({
    selector: 'app-expansion-panel',
    templateUrl: 'app-expansion-panel.html'
})

export class AppExpansionPanelComponent implements OnInit {

    @HostBinding('class.card') card= true;
    @HostBinding('class.imc--expansion-panel') expansion_panel= true;
    @Input() title: string;
    @Input() subtitle: string;
    @Input() allow_expansion: boolean = true;

    panel_is_expanded = true;
    panel_id: string;

    constructor() {
    }

    panel_expand(){
        this.panel_is_expanded = !this.panel_is_expanded;
    }

    static _rnd () {
        return Math.floor((1 + Math.random()) * 0x10000).toString(16);
    }

    ngOnInit() {
        this.panel_id = `panel_${AppExpansionPanelComponent._rnd()}${AppExpansionPanelComponent._rnd()}`;
    }

}