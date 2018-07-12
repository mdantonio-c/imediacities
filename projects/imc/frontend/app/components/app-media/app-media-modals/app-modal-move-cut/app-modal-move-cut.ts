import { Component, OnChanges, AfterViewInit, Input, ViewChild } from '@angular/core';
import { AppMediaModal } from "../app-media-modal";
import { ShotRevisionService } from "../../../../services/shot-revision.service";

@Component({
	selector: 'app-modal-move-cut',
	templateUrl: 'app-modal-move-cut.html',
	providers: [ShotRevisionService]
})
export class AppModalMoveCutComponent implements OnChanges, AfterViewInit {

	@Input() data: any;

	media_type: string = 'video';
	changed: boolean = false;
	shots: any[] = [];
	current_cut: number;

	@ViewChild(AppMediaModal) media: AppMediaModal;

	constructor(private shotRevisionService: ShotRevisionService) {
		shotRevisionService.cutChanged$.subscribe(
			cut => { this.change_cut(cut); }
		);
	}

	player_seek_at(frameIdx) {
		this.media.videoPlayer.jump_to(frameIdx, true);
	}

	private change_cut(newFrameIdx) {
		if (this.current_cut === newFrameIdx) { return; }
		this.current_cut = newFrameIdx;
		if (this.shots[1].attributes.start_frame_idx !== this.current_cut) {
			this.changed = true;
		}
		console.log('cut moved to frame', this.current_cut);

	}

	private update_shots() {
		this.shots[0].attributes.end_frame_idx = this.current_cut - 1;
		this.shots[1].attributes.start_frame_idx = this.current_cut;
		// should update timestamp?
		// TODO
	}

	ok() {
		this.update_shots();
		this.media.chiudi();
	}

	ngOnChanges() {
		this.shots = this.data.shots;
		this.current_cut = this.shots[1].attributes.start_frame_idx;
	}

	ngAfterViewInit() {
		this.media.videoPlayer.range.set({
			index: this.shots[0].attributes.shot_num,
			start: this.shots[0].attributes.start_frame_idx,
			end: this.shots[1].attributes.end_frame_idx,
			loop: true,
			video: this.media.videoPlayer
		});
		// position the video cursor on the current cut
		this.player_seek_at(this.current_cut);
	}
}