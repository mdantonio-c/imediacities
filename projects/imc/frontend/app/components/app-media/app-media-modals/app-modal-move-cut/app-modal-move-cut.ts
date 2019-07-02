import { Component, OnChanges, AfterViewInit, OnDestroy, Input, ViewChild } from '@angular/core';
import { AppMediaModal } from "../app-media-modal";
import { ShotRevisionService } from "../../../../services/shot-revision.service";
import { AppVideoService } from "../../../../services/app-video";
import { Subscription }   from 'rxjs';

@Component({
	selector: 'app-modal-move-cut',
	templateUrl: 'app-modal-move-cut.html'
})
export class AppModalMoveCutComponent implements AfterViewInit, OnChanges, OnDestroy {

	@Input() data: any;
	@Input() current_cut: number;

	changed: boolean = false;
	shots: any[] = [];
	subscription: Subscription;
	
	private fps;
	private split = false;

	@ViewChild(AppMediaModal, { static: false }) modal: AppMediaModal;

	constructor(
		private shotRevisionService: ShotRevisionService,
		private videoService: AppVideoService)
	{
		this.subscription = shotRevisionService.cutChanged$.subscribe(
			cut => { this.change_cut(cut); }
		);
	}

	player_seek_at(frameIdx:number): void {
		this.modal.videoPlayer.jump_to(frameIdx, true);
	}

	private change_cut(newFrameIdx: number): void {
		if (this.current_cut === newFrameIdx) { return; }
		this.current_cut = newFrameIdx;
		if (this.shots[1].attributes.start_frame_idx !== this.current_cut) {
			this.changed = true;
			this.shots[0].attributes.end_frame_idx = this.current_cut - 1;
			this.shots[1].attributes.start_frame_idx = this.current_cut;
			// should update timestamp
			this.shots[1].attributes.timestamp = this.shotRevisionService.shot_timestamp(this.current_cut, this.fps);
			// should update duration
			this.shots[0].attributes.duration = this.shotRevisionService.shot_duration(this.shots[0], this.fps);
			this.shots[1].attributes.duration = this.shotRevisionService.shot_duration(this.shots[1], this.fps);
		}
		/*console.log('cut moved to frame', this.current_cut);*/
	}

	private update_shots(): void {
		this.data.shots[0].attributes.end_frame_idx = this.shots[0].attributes.end_frame_idx;
		this.data.shots[0].attributes.duration = this.shots[0].attributes.duration;
		if (this.split) {
			this.shotRevisionService.addCut(this.shots);
			return;
		}

		this.data.shots[1].attributes.start_frame_idx = this.shots[1].attributes.start_frame_idx;
		this.data.shots[1].attributes.timestamp = this.shots[1].attributes.timestamp;
		this.data.shots[1].attributes.duration = this.shots[1].attributes.duration;
		this.data.shots[1].attributes.revision_confirmed = true;
	}

	ok() {
		this.update_shots();
		this.modal.chiudi();
	}

	ngOnChanges() {
		/* init component */
		this.fps = this.videoService.fps();
		this.changed = false;
		this.shots = [];
		this.split = false;
		
		if (this.data.shots.length === 1) {
			// expected exactly one shot for 'add cut'
			let shot = this.data.shots[0];
			// set the cut in the middle
			this.current_cut = 
				shot.attributes.start_frame_idx + Math.floor((shot.attributes.end_frame_idx - shot.attributes.start_frame_idx) / 2) + 1;
			// split the shot
			this.shots = this.split_shot(shot, this.current_cut);
			/*console.log('shot[0]', JSON.stringify(this.shots[0]));
			console.log('shot[1]', JSON.stringify(this.shots[1]));*/
			this.changed = true;
			this.split = true;
		} else {
			// expected exactly two shots for move cut
			this.shots = this.clone_shots();
			this.current_cut = this.shots[1].attributes.start_frame_idx;
			this.changed = false;
			this.split = false;
		}
		if (this.modal.videoPlayer) { this.init_player(); }
	}

	private clone_shots() {
		let shot_1 = JSON.parse(JSON.stringify(this.data.shots[0]));
		let shot_2 = JSON.parse(JSON.stringify(this.data.shots[1]));
		return [shot_1, shot_2];
	}

	/* */
	private split_shot(shot: any, cut: number): any[] {
		let shot_1 = JSON.parse(JSON.stringify(shot));
		// update shot 1
		shot_1.attributes.end_frame_idx = cut -1;
		shot_1.attributes.duration = this.shotRevisionService.shot_duration(shot_1, this.fps);
		// create a new shot 2
		let shot_2 = {
			id: null,
			links: null,
			attivo: false,
			attributes: {
				shot_num: shot_1.attributes.shot_num + 1,
				start_frame_idx: cut,
				end_frame_idx: shot.attributes.end_frame_idx,
				timestamp: this.shotRevisionService.shot_timestamp(cut, this.fps),
				duration: null
			},
			annotations: {
				links: [],
				locations: [],
				notes: [],
				references: [],
				tags: []
			}
		}
		shot_2.attributes.duration = this.shotRevisionService.shot_duration(shot_2, this.fps);
		return [shot_1, shot_2];
	}

	ngAfterViewInit() {
		this.init_player();
	}

	ngOnDestroy() {
   		// prevent memory leak when component destroyed
    	this.subscription.unsubscribe();
  	}

	private init_player() {
		this.modal.videoPlayer.range.set({
			index: this.shots[0].attributes.shot_num,
			start: this.shots[0].attributes.start_frame_idx,
			end: this.shots[1].attributes.end_frame_idx,
			loop: true,
			video: this.modal.videoPlayer
		});
		// position the video cursor on the current cut
		this.player_seek_at(this.current_cut);
	}
}