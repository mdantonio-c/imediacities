import {Component, Input, Output, EventEmitter, OnInit, OnChanges, ViewChild, ElementRef} from '@angular/core';
import {AppVideoControlComponent} from "../app-video-controls/app-video-control";

@Component({
    selector: 'app-video-shot',
    templateUrl: 'app-video-shot.html'
})

export class AppVideoShotComponent extends AppVideoControlComponent implements OnInit, OnChanges {

    @Input() shot;
    @Input() multiSelection;
    @Input() user;

    @Output() modale_richiedi: EventEmitter<any> = new EventEmitter();
    @Output() is_selezionato: EventEmitter<any> = new EventEmitter();

    public scene = null;

    public details_show = false;
    public checkbox_selection_label = 'multi-annotation';
    public collapse_id = 'collapse-details';
    public dropdown_id = 'dropdown';

    public is_attivo = false;

    constructor(
        private element: ElementRef) {
        super();
    }

    details_toggle(){
        this.details_show = !this.details_show;
        //  tdb scrolla quando viene espanso
        // if (this.details_show) {
        //     setTimeout( () => this.scroll(), 0);
        // }
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

    shot_play () {
        this.parent.shot_play(this.shot.attributes.shot_num);
    }

    shot_goto (frame, pause: true) {
        this.parent.jump_to(frame, true, pause)
    }

    shot_seleziona (evento) {
        this.is_selezionato.emit({
            index: this.shot.attributes.shot_num,
            stato: evento.target.checked
        })
    }

    scroll (set_attivo = false){

        let element = this.element.nativeElement;

        let h = element.getBoundingClientRect().height;
        if (set_attivo) {
            this.is_attivo = true;
        }
        this.scrollTo(element.parentElement.parentElement, h * this.shot.attributes.shot_num, 400);
    }

    tag_is_deletable (tag) {
        return tag.creator === this.user.uuid
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

    ngOnInit() {
        super.ngOnInit();
    }

    ngOnChanges () {
        // console.log("onchanges",this.shot.attributes.shot_num);
        // console.log("this.details_show",  this.details_show);
        this.scene = Object.assign({}, this.shot);
        // console.log("this.scene",  this.scene);

        this.checkbox_selection_label += this.shot.attributes.shot_num;
        this.collapse_id += this.shot.attributes.shot_num;
        this.dropdown_id += this.shot.attributes.shot_num;
    }

    onshot_start (e) {

        if (e.attributes.shot_num === this.shot.attributes.shot_num) {
            setTimeout( () => this.scroll(true), 0);
        } else {
            this.is_attivo = false;
        }
    }


}