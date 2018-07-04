import { Directive, ElementRef, HostListener } from '@angular/core';
import {NgModel} from '@angular/forms';

@Directive({selector: '[inputNumeric]'})
export class InputNumericDirective {

    constructor(private el: ElementRef, public model: NgModel) {
    }



    @HostListener('keydown', ['$event']) onKeyDown(event) {
        let e = <KeyboardEvent> event;

        if ([46, 8, 9, 27, 13, 110, 190].indexOf(e.keyCode) !== -1 ||
            // Allow: Ctrl+A
            (e.keyCode === 65 && (e.ctrlKey || e.metaKey)) ||
            // Allow: Ctrl+C
            (e.keyCode === 67 && (e.ctrlKey || e.metaKey)) ||
            // Allow: Ctrl+V
            (e.keyCode === 86 && (e.ctrlKey || e.metaKey)) ||
            // Allow: Ctrl+X
            (e.keyCode === 88 && (e.ctrlKey || e.metaKey)) ||
            // Allow: home, end, left, right
            (e.keyCode >= 35 && e.keyCode <= 39)) {
            // let it happen, don't do anything
            return;
        }

        if (this.el.nativeElement.value && !isNaN(this.el.nativeElement.value) && (e.keyCode === 187 || e.keyCode === 189)) {

            let amount = 1;

            if (e.shiftKey) {
                amount = 10
            }

            if (e.ctrlKey) {
                amount = 100;
            }

            if (e.altKey) {
                amount = 1000;
            }

            //  meno
            if (e.keyCode === 189) {
                amount *= -1;
            }

            if (parseInt(this.el.nativeElement.value) + amount >= 0) {
                this.el.nativeElement.value = parseInt(this.el.nativeElement.value) + amount;
                this.model.valueAccessor.writeValue(this.el.nativeElement.value);
                this.el.nativeElement.dispatchEvent(new Event('input'))
            }

        }

        // Ensure that it is a number and stop the keypress
        if ((e.shiftKey || (e.keyCode < 48 || e.keyCode > 57)) && (e.keyCode < 96 || e.keyCode > 105)) {
            e.preventDefault();
        }
    }
}