import { Directive, ElementRef, HostListener } from "@angular/core";

@Directive({ selector: "[inputSelect]" })
export class InputSelectDirective {
  constructor(private el: ElementRef) {}

  @HostListener("click", ["$event"]) onClick(event) {
    this.el.nativeElement.setSelectionRange(
      0,
      this.el.nativeElement.value.length
    );
  }
}
