import { Injectable } from '@angular/core';
import { ApiService } from '/rapydo/src/app/services/api';
import { Subject } from 'rxjs';
import * as moment from 'moment';

@Injectable()
export class ShotRevisionService {

	private _underRevision: boolean = false;

	private cutChangedSource = new Subject<number>();
	private cutAddedSource = new Subject<any[]>();

	constructor(private api: ApiService) {
	}

	cutChanged$ = this.cutChangedSource.asObservable();
	cutAdded$ = this.cutAddedSource.asObservable();

	changeCut(newCut: number) {
		this.cutChangedSource.next(newCut);
	}

	addCut(shots: any[]) {
		this.cutAddedSource.next(shots);
	}

	shot_duration(shot: any, fps: number): number {
		return (shot.attributes.end_frame_idx - shot.attributes.start_frame_idx + 1) / fps;
	}

	shot_timestamp(frame: number, fps: number): string {
		let seconds = Math.floor(frame / fps);
		let remainder = frame % fps
		let timestamp = moment().startOf('day')
			.seconds(seconds)
			.format('HH:mm:ss');
		return timestamp = timestamp + '-f' + remainder;
	}

	exitRevision(videoId, cb) {
		if (!cb || typeof cb !== 'function') {
            console.log("ShotRevisionService", "Callback mancante");
            return
        }

		this.api.delete(
            'videos/'+videoId+'/shot-revision'
        ).subscribe(
            response => {
            	console.log('video ['+videoId+'] exit from revision');
                cb();
            },
            err => {}
        );
	}

	putVideoUnderRevision(videoId, cb) {
		if (!cb || typeof cb !== 'function') {
            console.log("ShotRevisionService", "Callback mancante");
            return
        }

		this.api.put(
            'videos/'+videoId+'/shot-revision'
        ).subscribe(
            response => {
            	console.log('video ['+videoId+'] is now under revision');
            	cb();
            },
            err => {}
        );
	}
}