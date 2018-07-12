import { Injectable } from '@angular/core';
import { Subject } from 'rxjs';

/*export interface CutChangeEvent { }*/

@Injectable()
export class ShotRevisionService {

	private _underRevision: boolean = false;

	// Observable number source
	private cutChangedSource = new Subject<number>();

	// Observable string streams
	cutChanged$ = this.cutChangedSource.asObservable();

	// Service message commands
	changeCut(newCut: number) {
		this.cutChangedSource.next(newCut);
	}
}