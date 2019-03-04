/**
 *
 * Questa diretticva serve a forzare il posizionamento assoluto del dropdown
 * in modo da risolvere problemi di clipping dovuti all'overflow dell'elemento che contiene il dropdown
 *
 * Rif: https://github.com/ng-bootstrap/ng-bootstrap/issues/1012
 *
 */
import {Directive, ContentChild, AfterContentInit, ElementRef, OnDestroy, Inject, forwardRef} from '@angular/core';
import {NgbDropdownMenu, NgbDropdown} from '@ng-bootstrap/ng-bootstrap';
import {positionElements} from '@ng-bootstrap/ng-bootstrap/esm5/util/positioning';
import {Subscription} from 'rxjs/Subscription';

@Directive({
    selector: '[ngbDropdown][ngbDropdownReposition]',
})
export class DropdownPositionDirective implements AfterContentInit, OnDestroy {

    @ContentChild(NgbDropdownMenu) private menu: NgbDropdownMenu;
    @ContentChild(NgbDropdownMenu, {read: ElementRef}) private menuRef: ElementRef;


    private oldParent: HTMLElement | null;
    private menuWrapper: HTMLElement;
    private onChangeSubscription: Subscription;

    constructor(
        @Inject(forwardRef(() => NgbDropdown)) private dropdown: NgbDropdown,
        private elementRef: ElementRef,
    ) {
        this.onChangeSubscription = this.dropdown.openChange.subscribe((open: boolean) => {
            if (!open) {
                setTimeout(() => this.removeMenuFromBody(), 0);
            } else {
                if (!this.isInBody()) {
                    this.appendMenuToBody();
                }
            }
        });
    }

    ngAfterContentInit() {
        this.oldParent = (<HTMLElement> this.menuRef.nativeElement).parentElement;
        this.createWrapper();
        this.menu.position = (triggerEl: HTMLElement, placement: string) => {
            this.setWrapperWidth();
            this.menu.applyPlacement(
                positionElements(triggerEl, this.menuWrapper, placement, true));
        };
        //  That's a pezza
        //  Aggiungo al wrapper creato dalla direttiva le classi dell'oggetto originale
        //  Tra le classi assegnate all'oggetto originale prendo solo quelle che contengono la stringa 'dropdown'
        for (let c = 0; c < this.oldParent.classList.length; c++) {
            if (this.oldParent.classList[c].indexOf('dropdown') !== -1) {
                this.menuWrapper.classList.add(this.oldParent.classList[c])
            }
        }
    }

    ngOnDestroy() {
        this.removeMenuFromBody();
        if (this.onChangeSubscription) {
            this.onChangeSubscription.unsubscribe();
        }
    }

    private isInBody() {
        return this.menuWrapper.parentNode === document.body;
    }

    private removeMenuFromBody() {
        if (this.isInBody()) {
            if (this.oldParent) {
                this.oldParent.appendChild(this.menuWrapper);
            }
        }
    }

    private appendMenuToBody() {
        window.document.body.appendChild(this.menuWrapper);
    }

    private createWrapper() {
        this.menuWrapper = document.createElement('div');
        this.menuWrapper.style.position = 'absolute';
        this.menuWrapper.style.zIndex = '1000';

        this.menuWrapper.addEventListener('keyup', (event: KeyboardEvent) => {
            if (event.keyCode === 27) {
                this.dropdown.close();
            }
        });
        this.menuWrapper.appendChild(this.menuRef.nativeElement);
    }

    private setWrapperWidth() {
        const parentEl = <HTMLElement> this.elementRef.nativeElement;
        this.menuWrapper.style.width = parentEl.clientWidth + 'px';
    }
}