import { Component, Input, Output, EventEmitter, OnInit, OnChanges, ViewChild, ElementRef } from '@angular/core';
import { AppVideoControlComponent } from "../app-video-controls/app-video-control";
import { is_annotation_owner } from "../../../decorators/app-annotation-owner";

@Component({
    selector: 'app-video-shot',
    templateUrl: 'app-video-shot.html'
})
export class AppVideoShotComponent extends AppVideoControlComponent implements OnInit, OnChanges {

    @Input() shot: any;
    @Input() multiSelection: boolean = false;
    @Input() user;
    @Input() media_type = 'video';
    @Input() shotRevision: boolean = false;
    @Input() shotRevisionState: string = '';
    @Input() tot_num_shots: number;

    @Output() modale_richiedi: EventEmitter<any> = new EventEmitter<any>();
    @Output() is_selezionato: EventEmitter<any> = new EventEmitter<any>();
    @Output() revise_shot: EventEmitter<any> = new EventEmitter<any>();

    @is_annotation_owner() is_annotation_owner;

    public scene = null;

    public arrow_icon = false;
    public checkbox_selection_label = 'multi-annotation';
    public collapse_id = 'collapse-details';
    public dropdown_id = 'dropdown';

    public is_attivo = false;
    public details_open = false;

    constructor(
        private element: ElementRef) {
        super();
    }

    details_toggle() {
        this.arrow_icon = !this.arrow_icon;
        this.details_open = !this.details_open;
    }

    details_show() {
        this.details_open = true;
        this.arrow_icon = true;
    }

    modale_show(event, modale) {
        if (event.target) {
            this.modale_richiedi.emit({
                modale: modale,
                titolo: event.target.innerText,
                data: { shots: [this.shot] },
                next: event.next ? true : false
            });
        }
    }

    shot_play() {
        if (this.media_type !== 'video') return;
        this.parent.shot_play(this.shot.attributes.shot_num);
    }

    shot_goto(frame, pause: true) {
        this.parent.jump_to(frame, true, pause)
    }

    shot_seleziona(evento) {
        this.is_selezionato.emit({
            index: this.shot.attributes.shot_num,
            stato: evento.target.checked
        })
    }

    scroll(set_attivo = false) {

        let element = this.element.nativeElement;

        let h = element.getBoundingClientRect().height;
        if (set_attivo) {
            this.is_attivo = true;
            this.details_open = true;
        }

        if (element.parentElement === undefined) { return; }
        this.scrollTo(element.parentElement.parentElement, h * this.shot.attributes.shot_num, 400);
    }

    tag_is_deletable(tag) {
        return this.is_annotation_owner(this.user, tag.creator);
    }

    scrollTo(element, to, duration) {

        let start = element.scrollTop;
        let change = to - start;
        let currentTime = 0;
        let increment = 20;

        let animateScroll = () => {
            currentTime += increment;
            element.scrollTop = this.easeInOutQuad(currentTime, start, change, duration);
            if (currentTime < duration) {
                setTimeout(animateScroll, increment);
            }
        };
        animateScroll();
    }

    remove_upper_cut() {
        console.log('remove upper cut for shot', this.shot);
        this.revise_shot.emit({
            op: 'join',
            index: this.shot.attributes.shot_num,
        });
    }

    move_cut() {
        // move to the first frame of the next shot
        this.parent.jump_to(this.shot.attributes.end_frame_idx+1, true, true);
    }

    //t = current time
    //b = start value
    //c = change in value
    //d = duration
    easeInOutQuad = function(t, b, c, d) {
        t /= d / 2;
        if (t < 1) return c / 2 * t * t + b;
        t--;
        return -c / 2 * (t * (t - 2) - 1) + b;
    };

    ngOnInit() {
        super.ngOnInit();
    }

    ngOnChanges() {

        this.scene = Object.assign({}, this.shot);
        // console.log("this.scene",  this.scene);

        this.checkbox_selection_label += this.shot.attributes.shot_num;
        this.collapse_id += this.shot.attributes.shot_num;
        this.dropdown_id += this.shot.attributes.shot_num;
    }

    onshot_start(e) {

        if (e.attributes.shot_num === this.shot.attributes.shot_num) {
            setTimeout(() => this.scroll(true), 0);
        } else {
            this.is_attivo = false;
            this.details_open = false;
        }
    }

}