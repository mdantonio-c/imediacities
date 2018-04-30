import {Component, Input, Output, EventEmitter, OnInit, ViewChild, ElementRef} from '@angular/core';
import {AppVideoControlComponent} from "../app-video-controls/app-video-control";

@Component({
    selector: 'app-video-shot',
    templateUrl: 'app-video-shot.html'
})

export class AppVideoShotComponent extends AppVideoControlComponent implements OnInit {

    @Input() shot;
    @Input() multiSelection;

    @Output() modale_richiedi: EventEmitter<any> = new EventEmitter();
    @Output() is_selezionato: EventEmitter<any> = new EventEmitter();

    public details_show = false;
    public checkbox_selection_label = 'multi-annotation';
    public collapse_id = 'collapse-details';

    public is_attivo = false;

    constructor(private element: ElementRef) {
        super();
    }

    details_toggle(stato = null){
        this.details_show = stato ? stato : !this.details_show
    }

    modale_show (evento, modale) {

        if (evento.target) {
            this.modale_richiedi.emit({
                modale: modale,
                titolo: evento.target.innerText,
                data: {shots: [this.shot]}
            });

        }

    }

    play_scene () {
        this.parent.shot_play(this.shot.attributes.shot_num);
    }

    shot_seleziona (evento) {
        this.is_selezionato.emit({
            index: this.shot.attributes.shot_num,
            stato: evento.target.checked
        })
    }

    ngOnInit() {
        super.ngOnInit();
        this.checkbox_selection_label += this.shot.attributes.shot_num;
        this.collapse_id += this.shot.attributes.shot_num;
    }

    onshot_start (e) {

        if (e.attributes.shot_num === this.shot.attributes.shot_num) {
            setTimeout( () => this.scroll(), 0);
        } else {
            this.is_attivo = false;
        }
    }

    scroll (){

        let element = this.element.nativeElement;

        let h = element.getBoundingClientRect().height;
        this.is_attivo = true;
        this.scrollTo(element.parentElement.parentElement, h * this.shot.attributes.shot_num, 400);
    }

    scrollTo (element, to, duration) {

        let start = element.scrollTop;
        let change = to - start;
        let currentTime = 0;
        let increment = 20;

        let animateScroll = () => {
            currentTime += increment;
            element.scrollTop = this.easeInOutQuad(currentTime, start, change, duration);
            if(currentTime < duration) {
                setTimeout(animateScroll, increment);
            }
        };
        animateScroll();
    }

    //t = current time
    //b = start value
    //c = change in value
    //d = duration
    easeInOutQuad = function (t, b, c, d) {
        t /= d/2;
        if (t < 1) return c/2*t*t + b;
        t--;
        return -c/2 * (t*(t-2) - 1) + b;
    };

}