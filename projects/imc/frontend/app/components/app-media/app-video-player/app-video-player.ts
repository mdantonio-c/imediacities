import {
  Component,
  Input,
  ViewChild,
  ViewChildren,
  OnInit,
  AfterViewInit,
  Output,
  ElementRef,
  EventEmitter,
  ChangeDetectorRef,
} from "@angular/core";
import { rangePlayer } from "../../../decorators/app-range";
import { ShotRevisionService } from "../../../services/shot-revision.service";
import { AuthService } from "@rapydo/services/auth";
import { NgxSpinnerService } from "ngx-spinner";

@Component({
  selector: "app-video-player",
  templateUrl: "app-video-player.html",
})
export class AppVideoPlayerComponent implements OnInit, AfterViewInit {
  @Input() data: any;
  @Input() shots: any;
  @Input() layout: any = "main";
  @Input() revision: boolean = false;

  @Output() video_player_ready: EventEmitter<any> = new EventEmitter<any>();

  @ViewChild("videoPlayer", { static: false }) videoPlayer: ElementRef;

  advanced_show = false;

  componenti = new Array();

  fps = 0;
  frame_length = 0;

  showComponents = false;
  video = null;

  metadata = null;
  player = null;

  spinner_prevent = false;
  shot_current = -1;

  /**
   * Stores the point from which to restart in the case of a range in loop
   * @type {number}
   */
  restart_time = null;

  constructor(
    private cdRef: ChangeDetectorRef,
    private elRef: ElementRef,
    private shotRevisionService: ShotRevisionService,
    private auth: AuthService,
    private spinner: NgxSpinnerService
  ) {}

  @rangePlayer() range;

  _frame_set(f) {
    let fr = f.split("/");
    if (fr.length == 1) {
      console.log(`Cannot determine frame rate from ${f}`);
      // This is my default in case of problems...
      this.fps = 25;
    } else {
      this.fps = Number(fr[0]);
    }
    // sporchissimo :)
    // this.fps = eval(f);
    this.frame_length = 1 / this.fps;
  }

  _video_source_add(source_url) {
    let token = this.auth.getToken();
    let source = document.createElement("source");
    let append = token !== null ? "&access_token=" + token : "";
    source.src = source_url + append;
    this.videoPlayer.nativeElement.appendChild(source);
    this.video.load();
  }

  _video_events() {
    this.video.onended = (e) => {
      this._emetti("onended", e);
    };

    this.video.onfullscreen = (e) => {
      this._emetti("onfullscreen", e);
    };

    this.video.onloadeddata = (e) => {
      this._emetti("onloadeddata", e);
    };

    this.video.onloadedmetadata = (e) => {
      this.metadata = {
        begin: 0,
        duration: this.video.duration,
      };

      if (this.player === null) {
        this.player = {
          begin: 0,
          duration: this.video.duration,
        };
      }
      this.showComponents = true;
      this._emetti("onloadedmetadata", e);
    };

    this.video.onloadstart = (e) => {
      this.spinner.show();
      this._emetti("onloadstart", e);
    };

    this.video.oncanplay = (e) => {
      this.spinner.hide();
    };

    this.video.onpause = (e) => {
      this._emetti("onpause", e);
    };

    this.video.onplay = (e) => {
      this.spinner_prevent = false;
      this._emetti("onplay", e);
    };

    this.video.onplaying = (e) => {
      this._emetti("onplaying", e);
    };

    this.video.onprogress = (e) => {
      this._emetti("onprogress", e);
      //  todo componentizzare
      this.elRef.nativeElement
        .querySelector(".video_mask")
        .classList.remove("video_mask--active");
    };

    this.video.onseeked = (e) => {
      this._emetti("onseeked", e);
      if (this.spinner_prevent) return;
      //  todo componentizzare
      this.elRef.nativeElement
        .querySelector(".video_mask")
        .classList.remove("video_mask--active");
    };

    this.video.onseeking = (e) => {
      this._emetti("onseeking", e);
      if (this.spinner_prevent) return;
      //  todo componentizzare
      this.elRef.nativeElement
        .querySelector(".video_mask")
        .classList.add("video_mask--active");
    };

    this.video.ontimeupdate = (e) => {
      this._emetti("ontimeupdate", e);

      // if(this.video.currentTime == 0){

      if (this.player) {
        //  Evento onbegin
        //  inizio del filmato o del range
        if (this.video.currentTime <= this.player.begin) {
          this._emetti("onbegin", e);
        }

        //  Evento onended
        //  fine del filmato o del range
        if (
          this.video.currentTime >=
          this.player.begin + this.player.duration
        ) {
          this._emetti("onended", e);
        }

        //  Rilevamento shots
        let current_frame = Math.ceil(this.fps * this.video.currentTime);
        let shot_corrente = 0;
        this.shots.forEach((s, idx) => {
          if (
            current_frame >= s.start_frame_idx &&
            current_frame <= s.end_frame_idx
          ) {
            s.attivo = true;
            shot_corrente = idx;
          } else {
            s.attivo = false;
          }
        });

        if (this.shot_current !== shot_corrente) {
          this.shot_current = shot_corrente;
          this._emetti("onshot_start", this.shots[shot_corrente]);
        }
      }
    };

    this.video.onvolumechange = (e) => {
      this._emetti("onvolumechange", e);
    };

    this.video.onwaiting = (e) => {
      this._emetti("onwaiting", e);
    };
  }

  _emetti(evento, dati) {
    this.componenti.forEach((c) => {
      c[evento](dati);
    });
  }

  _play_interval(intervallo) {}

  public jump_to(time_or_frames, um_is_frame = false, pause = false) {
    if (pause) {
      this.video.pause();
    }

    if (um_is_frame) {
      time_or_frames = this.frame_to_time(time_or_frames);
    }
    this.video.currentTime = time_or_frames;
  }

  public shot_play(shot_number) {
    // jump by time (?)
    //this.jump_to(1 / this.fps * this.shots[shot_number].start_frame_idx);
    // always jump by frame
    this.jump_to(this.shots[shot_number].start_frame_idx, true);
  }

  public segment_play(segment) {}

  public registra(componente) {
    this.componenti.push(componente);
  }

  public fullscreen(stato) {
    this.elRef.nativeElement.children[0]
      .querySelector(".video_container")
      .classList[stato === "on" ? "add" : "remove"](
        "video_container--fullscreen"
      );
  }

  public remove() {
    this.video.remove();
  }

  /**
   * Returns the current SMPTE Time code in the video.
   * - Can be used as a conversion utility.
   *
   * @param  {Number} frame - Frame number for conversion to it's equivalent SMPTE Time code.
   * @return {String} Returns a SMPTE Time code in HH:MM:SS:FF format
   */
  toSMPTE = function (frame) {
    // if (!frame) { return this.toTime(this.video.currentTime); }
    var frameNumber = Number(frame);
    var fps = this.fps;
    function wrap(n) {
      return n < 10 ? "0" + n : n;
    }
    var _hour = fps * 60 * 60,
      _minute = fps * 60;
    var _hours = (frameNumber / _hour).toFixed(0);
    var _minutes =
      Number((frameNumber / _minute).toString().split(".")[0]) % 60;
    var _seconds = Number((frameNumber / fps).toString().split(".")[0]) % 60;
    var SMPTE =
      wrap(_hours) +
      ":" +
      wrap(_minutes) +
      ":" +
      wrap(_seconds) +
      ":" +
      wrap(frameNumber % fps);
    return SMPTE;
  };

  /**
   * Returns the time in the video for a given frame number
   *
   * @param  {Number} frame - The frame number in the video to seek to.
   * @return {Number} - Time in seconds
   */
  frame_to_time(frame) {
    /* To seek forward in the video, we must add 0.001 to the video runtime for proper interactivity */
    //return (frame * this.frame_length) + 0.001;

    // this seems to work better
    return (Number(frame) + 0.6) * this.frame_length;
  }

  /**
   * Converts a SMPTE Time code to Seconds
   *
   * @param  {String} SMPTE - a SMPTE time code in HH:MM:SS:FF format
   * @return {Number} Returns the Second count of a SMPTE Time code
   */
  toSeconds(SMPTE) {
    if (!SMPTE) {
      return Math.floor(this.video.currentTime);
    }
    var time = SMPTE.split(":");
    return Number(time[0]) * 60 * 60 + Number(time[1]) * 60 + Number(time[2]);
  }

  /**
   * Converts a SMPTE Time code, or standard time code to Milliseconds
   *
   * @param  {String} SMPTE a SMPTE time code in HH:MM:SS:FF format,
   * or standard time code in HH:MM:SS format.
   * @return {Number} Returns the Millisecond count of a SMPTE Time code
   */
  toMilliseconds(SMPTE) {
    var frames = Number(SMPTE.split(":")[3]);
    var milliseconds = (1000 / this.fps) * (isNaN(frames) ? 0 : frames);
    return Math.floor(this.toSeconds(SMPTE) * 1000 + milliseconds);
  }

  /**
   * Returns the frame number for a given time
   *
   * @param  {Number} time - The time in the video in seconds
   * @return {Number} - Frame number in video
   */
  time_to_frame(time) {
    return Math.floor(time.toFixed(5) / this.frame_length);
  }

  frame_current() {
    return this.time_to_frame(this.video.currentTime);
  }

  cut_changed() {
    this.shotRevisionService.changeCut(this.frame_current());
  }

  _floor(number, decimal_places) {
    return (
      Math.floor(parseFloat(number) * Math.pow(10, decimal_places)) /
      Math.pow(10, decimal_places)
    );
  }

  _round(number, decimal_places) {
    return (
      Math.round(parseFloat(number) * Math.pow(10, decimal_places)) /
      Math.pow(10, decimal_places)
    );
  }

  _round_fixed(number, decimal_places) {
    return this._round(number, decimal_places).toFixed(decimal_places);
  }

  _ceil(number, decimal_places) {
    return (
      Math.ceil(parseFloat(number) * Math.pow(10, decimal_places)) /
      Math.pow(10, decimal_places)
    );
  }

  public layout_check(layout) {
    return this.shots && this.shots.length && this.layout === layout;
  }

  public advanced_control_show(stato) {
    this.advanced_show = stato;
  }

  disableSaveAs(event) {
    return false;
  }

  ngOnInit() {
    this._frame_set(this.data._item[0].framerate);
  }

  ngAfterViewInit() {
    if (this.layout) {
      this.elRef.nativeElement.children[0].classList.add(
        `video_container--${this.layout}`
      );
    }

    this.video = this.videoPlayer.nativeElement;

    this._video_source_add(this.data.links.content);
    this._video_events();

    this.video_player_ready.emit(this);

    this.cdRef.detectChanges();
  }
}
