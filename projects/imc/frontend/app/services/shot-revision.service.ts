import { Injectable } from '@angular/core';
import { ApiService } from '@rapydo/services/api';
import { Subject } from 'rxjs';
import * as moment from 'moment';

export interface SceneCut {
	shot_num: number;
	cut?: number;
	annotations?: string[];
	confirmed?: boolean;
}

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
		return (shot.end_frame_idx - shot.start_frame_idx + 1) / fps;
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
            resp => {
            	console.log('video ['+videoId+'] exit from revision');
                cb();
            },
            err => {
            	cb(err);
            }
        );
	}

	putVideoUnderRevision(videoId: string, cb) {
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
            err => {
                cb(err);
            }
        );
	}

	reviseVideoShots(videoId: string, shots: SceneCut[], cb, exit=true) {
		if (!cb || typeof cb !== 'function') {
            console.log("ShotRevisionService", "Callback mancante");
            return
        }

        this.api.post(
            'videos/'+videoId+'/shot-revision',
            {
            	shots: shots,
            	exitRevision: exit
            }
        ).subscribe(
            response => {
            	console.log('shot revision for video ['+videoId+'] successfully completed');
            	cb();
            },
            err => {}
        );
	}
}