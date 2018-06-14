import {Component, ChangeDetectorRef, Input, OnInit, OnChanges} from '@angular/core';

enum AppInfoStato {
    SUCCESS = 'success',
    ERROR = 'error',
    INFO = 'info'
}

@Component({
    selector: 'app-info',
    templateUrl: 'app-info.html'
})

export class AppInfoComponent implements OnInit, OnChanges {

    @Input() message: string;
    @Input() result: string;
    @Input() visible: false;
    @Input() auto_hide = false;

    public icon: string;
    public classe: string;

    constructor(
        private ref: ChangeDetectorRef
    ) {
    }

    delete () {
        this.visible = false;
    }

    ngOnInit() {

    }

    ngOnChanges() {

        switch (this.result) {

            case AppInfoStato.SUCCESS:
                this.icon = 'done_all';
                break;
            case AppInfoStato.ERROR:
                this.icon = 'close';
                break;
            case AppInfoStato.INFO:
                this.icon = 'info';
                break;

        }

        this.classe = this.result;

        if (this.auto_hide) {
            setTimeout( () => this.delete(), 3500)
        }

        this.ref.detectChanges();
    }
}