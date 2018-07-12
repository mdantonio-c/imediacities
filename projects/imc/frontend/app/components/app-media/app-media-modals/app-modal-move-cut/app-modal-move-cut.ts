import { Component, OnChanges, AfterViewInit, Input, ViewChild } from '@angular/core';
import { AppMediaModal } from "../app-media-modal";
import { ShotRevisionService } from "../../../../services/shot-revision.service";
import * as moment from 'moment';

@Component({
	selector: 'app-modal-move-cut',
	templateUrl: 'app-modal-move-cut.html',
	providers: [ShotRevisionService]
})
export class AppModalMoveCutComponent implements OnChanges, AfterViewInit {

	@Input() data: any;

	changed: boolean = false;
	shots: any[] = [];
	current_cut: number;
	private fps;

	@ViewChild(AppMediaModal) modal: AppMediaModal;

	constructor(private shotRevisionService: ShotRevisionService) {
		shotRevisionService.cutChanged$.subscribe(
			cut => { this.change_cut(cut); }
		);
	}

	player_seek_at(frameIdx) {
		this.modal.videoPlayer.jump_to(frameIdx, true);
	}

	private change_cut(newFrameIdx) {
		if (this.current_cut === newFrameIdx) { return; }
		this.current_cut = newFrameIdx;
		if (this.shots[1].attributes.start_frame_idx !== this.current_cut) {
			this.changed = true;
		}
		/*console.log('cut moved to frame', this.current_cut);*/
	}

	private update_shots() {
		this.shots[0].attributes.end_frame_idx = this.current_cut - 1;
		this.shots[1].attributes.start_frame_idx = this.current_cut;
		// should update timestamp
		let seconds   = Math.floor(this.current_cut / this.fps);
		let remainder = this.current_cut % this.fps
		let timestamp = moment().startOf('day')
			.seconds(seconds)
			.format('HH:mm:ss');
		timestamp = timestamp + '-f' + remainder;
		this.shots[1].attributes.timestamp = timestamp;
		// should update duration
		this.shots[0].attributes.duration =
			(this.shots[0].attributes.end_frame_idx - this.shots[0].attributes.start_frame_idx) / this.fps;
		this.shots[1].attributes.duration =
			(this.shots[1].attributes.end_frame_idx - this.shots[1].attributes.start_frame_idx) / this.fps;
	}

	ok() {
		this.update_shots();
		this.modal.chiudi();
	}

	ngOnChanges() {
		// expected exactly two shots
		this.shots = this.data.shots;
		this.current_cut = this.shots[1].attributes.start_frame_idx;
		this.changed = false;
	}

	ngAfterViewInit() {
		this.modal.videoPlayer.range.set({
			index: this.shots[0].attributes.shot_num,
			start: this.shots[0].attributes.start_frame_idx,
			end: this.shots[1].attributes.end_frame_idx,
			loop: true,
			video: this.modal.videoPlayer
		});
		// position the video cursor on the current cut
		this.player_seek_at(this.current_cut);
		// get video frame rate
		this.fps = this.modal.videoPlayer.fps;
	}
}