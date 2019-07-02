import { Component, Input, ViewChild, OnInit, OnChanges, AfterViewInit, OnDestroy, ViewContainerRef } from '@angular/core';
import { AuthService } from "/rapydo/src/app/services/auth";
import { AppShotsService } from "../../../services/app-shots";
import { AppModaleService } from "../../../services/app-modale";
import { AppMediaService } from "../../../services/app-media";
import { AppVideoPlayerComponent } from "../app-video-player/app-video-player";

@Component({
    selector: 'app-media-modal',
    templateUrl: 'app-media-modal.html'
})
export class AppMediaModal implements OnInit, OnChanges, AfterViewInit, OnDestroy {

    @Input() data: any;
    @Input() media_type: string;
    @Input() revision: boolean = false;
    @ViewChild('videoPlayer', { static: false }) videoPlayer: AppVideoPlayerComponent;

    public mediaData = null;
    public shots = null;
    public shot_corrente = null;
    user: any;

    constructor(
        private auth: AuthService,
        private VideoService: AppMediaService,
        private ShotsService: AppShotsService,
        private ModalService: AppModaleService,
    ) { }

    /**
     * Consente di riprodurre uno shot cliccando sulla sua miniatura
     * @param shot_index
     */
    shot_cambia(shot_index) {

        if (!this.data || !this.data.shots || !this.data.shots.length) return;

        this.shot_corrente = this.data.shots[shot_index];

        if (!this.revision && this.videoPlayer && this.videoPlayer.video) {
            this.videoPlayer.range.set({
                index: this.shot_corrente.attributes.shot_num,
                start: this.shot_corrente.attributes.start_frame_idx,
                end: this.shot_corrente.attributes.end_frame_idx,
                loop: true,
                video: this.videoPlayer
            })
        }
    }

    /**
     * Chiude la modal
     */
    chiudi() {
        if (this.videoPlayer) {
            this.videoPlayer.video.pause();
        }
        (this.ModalService.get()).dismiss();
    }

    ngOnInit() {
        if (this.data.shots && this.data.shots.length) {
            this.shot_cambia(0);
        }
        this.user = this.auth.getUser();
    }

    ngOnChanges() {
        this.mediaData = this.VideoService.media();

        let token = this.auth.getToken();
        let append = (token !== null) ? '&access_token=' + token : '';
        let content = this.mediaData["links"]["content"];
        this.mediaData["links"]["content"] = content + append;

        this.shots = this.ShotsService.shots();
        this.shot_cambia(0);
    }

    ngAfterViewInit() {
        this.shot_cambia(0);
    }

    ngOnDestroy() {
        if (this.videoPlayer) {
            this.videoPlayer.remove();
        }
    }

}