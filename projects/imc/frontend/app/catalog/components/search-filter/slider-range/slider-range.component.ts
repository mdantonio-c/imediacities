import { Component, ElementRef, OnInit, Input, Output, EventEmitter, OnChanges, HostListener, Renderer2} from '@angular/core';

@Component({
	selector: 'slider-range',
	templateUrl: './slider-range.component.html',
	styleUrls: ['./slider-range.component.css']
})
export class SliderRangeComponent implements OnChanges, OnInit {
	@Input() min: number = 0;
	@Input() max: number = 100;
	@Input() step: number = 1;
	@Input('value-min') valueMin;
	@Input('value-max') valueMax;

	private dragging = false;
	private startPointXMin: number = 0;
	private startPointXMax: number = 0;
	private xPosMin = 0;
	private xPosMax = 0;

	@Output() change: EventEmitter<any> = new EventEmitter<true>();

	constructor(private el: ElementRef, private renderer: Renderer2) { }

	ngOnInit(): void {
		this.moveMin(this.valueMin);
		this.moveMax(this.valueMax);
	}

	private moveMin(value) {
		/*console.log('dragging? ' + this.dragging);*/
		if (this.dragging) return;
		let xPosMin = (value - this.min) / (this.max - this.min) * 100;
		if (xPosMin < 0) {
			xPosMin = 0;
		} else if (xPosMin > 100) {
			xPosMin = 100;
		}
		this.moveHandle("min", xPosMin);
		this.moveRange(xPosMin, this.xPosMax);
	}

	private moveMax(value) {
		/*console.log('dragging? ' + this.dragging);*/
		if (this.dragging) return;
		let xPosMax = (value - this.min) / (this.max - this.min) * 100;
		if (xPosMax < 0) {
			xPosMax = 0;
		} else if (xPosMax > 100) {
			xPosMax = 100;
		}
		this.moveHandle("max", xPosMax);
		this.moveRange(this.xPosMin, xPosMax);
	}

	ngOnChanges(changes: any) {
		if (this.dragging) return;
		if (changes.valueMin) { this.moveMin(changes.valueMin.currentValue); }
		if (changes.valueMax) { this.moveMax(changes.valueMax.currentValue); }
	}

	mouseDownMin($event) {
		/*console.log('mouse-down-min');
		console.log($event);*/
		this.dragging = true;
		this.startPointXMin = $event.pageX;
		/*console.log('dragging: ' + this.dragging);*/
	}

	mouseDownMax($event) {
		/*console.log('mouse-down-max');
		console.log($event);*/
		this.dragging = true;
		this.startPointXMax = $event.pageX;
		/*console.log('dragging: ' + this.dragging);*/
	}

	// Bind to full document, to make move easiery (not to lose focus on y axis)
	/*@HostListener('mousemove', ['$event']) onMouseMove($event) { */
	mouseMoveMax($event) {
		if (!this.dragging) return;
		// console.log($event);
		//Calculate handle position
		let moveDelta = $event.pageX - this.startPointXMax;
		console.log('moveDelta: ' + moveDelta);
		let clientWidth = this.el.nativeElement.querySelector('div').clientWidth;
		/*console.log('clientWidth: ' + clientWidth);*/
		console.log('current xPosMax: ' + this.xPosMax + ', current xPosMin: ' + this.xPosMin);
		let xPosMax = this.xPosMax + ((moveDelta / clientWidth) * 100);
		if (xPosMax > 100) {
			xPosMax = 100;
		} else if (xPosMax < this.xPosMin) {
			xPosMax = this.xPosMin;
		} else {
			// Prevent generating "lag" if moving outside window
			this.startPointXMax = $event.pageX;
		}
		console.log('new xPosMax: ' + xPosMax);
		// FIXME: UPDATE formControl input 
		this.valueMax = Math.round((((this.max - this.min) * (xPosMax / 100)) + this.min) / this.step) * this.step;
		console.log('valueMax: ' + this.valueMax);

		// Move the Handle
		this.moveHandle("max", xPosMax);
		this.moveRange(this.xPosMin, xPosMax);
	}

	mouseMoveMin($event) {
		// TODO
	}

	@HostListener('mouseup', ['$event']) onMouseUp() {
		this.dragging = false;
		console.log('dragging: ' + this.dragging);
		/*document.unbind('mousemove');
		document.unbind('mousemove');*/
	}

	// Move slider handle and range line
	private moveHandle = function(handle, posX) {
		let hdl = this.el.nativeElement.querySelector('.handle.' + handle);
		this.renderer.setStyle(hdl, 'left', posX + '%');
		/*this.el.nativeElement.querySelector('.handle.' + handle).style.left = posX + '%';*/
	};
	private moveRange = function(posMin, posMax) {
		let range = this.el.nativeElement.querySelector('.range');
		this.renderer.setStyle(range, 'left', posMin + '%');
		this.renderer.setStyle(range, 'width', posMax - posMin + '%');
		this.xPosMin = posMin;
		this.xPosMax = posMax;
	};
}