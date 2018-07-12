import { Component, OnInit } from '@angular/core';
import { AppVideoControlComponent } from "../app-video-control";

@Component({
    selector: 'app-video-control-step',
    templateUrl: 'app-video-control-step.html'
})
export class AppVideoControlStepComponent extends AppVideoControlComponent {

    step_value = 1;

    constructor() {
        super()
    }

    step_next() {
        if (this._step_is_valid()) {
            this.parent.jump_to(this.parent.frame_current() + parseInt(this.step_value.toString()), true);
        }
    }

    step_prev() {
        if (this._step_is_valid()) {
            this.parent.jump_to(this.parent.frame_current() - this.step_value, true);
        }
    }

    _step_is_valid() {
        return !isNaN(this.step_value);
    }

}