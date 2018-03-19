var __extends = (this && this.__extends) || (function () {
    var extendStatics = Object.setPrototypeOf ||
        ({ __proto__: [] } instanceof Array && function (d, b) { d.__proto__ = b; }) ||
        function (d, b) { for (var p in b) if (b.hasOwnProperty(p)) d[p] = b[p]; };
    return function (d, b) {
        extendStatics(d, b);
        function __() { this.constructor = d; }
        d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
    };
})();
var ControlloGenerico = /** @class */ (function () {
    function ControlloGenerico(conf) {
        this.element = conf.element;
        this.fps = conf.fps;
        this.frameLength = conf.frameLength;
        this.video = conf.video;
    }
    ControlloGenerico.prototype.onloadstart = function () { };
    ;
    ControlloGenerico.prototype.onloadeddata = function () { };
    ;
    ControlloGenerico.prototype.onplay = function () { };
    ;
    ControlloGenerico.prototype.onpause = function () { };
    ;
    ControlloGenerico.prototype.ontimeupdate = function () { };
    ;
    ControlloGenerico.prototype.onwaiting = function () { };
    ;
    ControlloGenerico.prototype.onplaying = function () { };
    ;
    ControlloGenerico.prototype.onseeked = function () { };
    ;
    ControlloGenerico.prototype.onended = function () { };
    ;
    ControlloGenerico.prototype.onvolumechange = function () { };
    //  custom events
    ControlloGenerico.prototype.onbegin = function () { }; //  il video è a currentTime = 0
    ControlloGenerico.prototype.onfullscreen = function () { }; //  il video è in fullscreen
    return ControlloGenerico;
}());
///<reference path="ControlloGenerico.ts"/>
var FpsChange = /** @class */ (function (_super) {
    __extends(FpsChange, _super);
    function FpsChange(conf) {
        var _this = _super.call(this, conf) || this;
        _this.element.onchange = function () {
            _this.change_fps(_this.element.value);
        };
        return _this;
    }
    FpsChange.prototype.change_fps = function (fps_to_set) {
        this.video.playbackRate = Utils.Round(fps_to_set / this.fps, 2);
    };
    return FpsChange;
}(ControlloGenerico));
///<reference path="ControlloGenerico.ts"/>
var FullScreen = /** @class */ (function (_super) {
    __extends(FullScreen, _super);
    function FullScreen(conf) {
        var _this = _super.call(this, conf) || this;
        _this.ICO_EXPAND = 0;
        _this.ICO_COMPRESS = 1;
        _this.video_wrapper = document.querySelector('.video_container');
        _this.icons = _this.element.querySelectorAll('span');
        _this.icons[_this.ICO_EXPAND].onclick = function () {
            _this.fullscreen();
        };
        _this.icons[_this.ICO_COMPRESS].onclick = function () {
            _this.fullscreen();
        };
        return _this;
    }
    FullScreen.prototype.fullscreen = function () {
        if (this.video_wrapper.classList.contains('video_container--fullscreen')) {
            //  rimuovi fullscreen
            this.video_wrapper.classList.remove('video_container--fullscreen');
            this.icons[this.ICO_EXPAND].classList.remove('display-none');
            this.icons[this.ICO_COMPRESS].classList.add('display-none');
        }
        else {
            //  vai in fullscreen
            this.video_wrapper.classList.add('video_container--fullscreen');
            this.icons[this.ICO_EXPAND].classList.add('display-none');
            this.icons[this.ICO_COMPRESS].classList.remove('display-none');
        }
    };
    return FullScreen;
}(ControlloGenerico));
///<reference path="ControlloGenerico.ts"/>
var GotoEndButton = /** @class */ (function (_super) {
    __extends(GotoEndButton, _super);
    function GotoEndButton(conf) {
        var _this = _super.call(this, conf) || this;
        _this.element.onclick = function () { _this.video.currentTime = _this.video.duration; };
        return _this;
    }
    return GotoEndButton;
}(ControlloGenerico));
///<reference path="ControlloGenerico.ts"/>
var GotoStartButton = /** @class */ (function (_super) {
    __extends(GotoStartButton, _super);
    function GotoStartButton(conf) {
        var _this = _super.call(this, conf) || this;
        _this.element.onclick = function () { _this.video.currentTime = 0; };
        return _this;
    }
    return GotoStartButton;
}(ControlloGenerico));
///<reference path="ControlloGenerico.ts"/>
var JumpControl = /** @class */ (function (_super) {
    __extends(JumpControl, _super);
    function JumpControl(conf) {
        var _this = _super.call(this, conf) || this;
        _this.um = conf.um || 'frames';
        _this.element.jump_to.onclick = function () {
            _this.jump_to();
        };
        _this.element.jump_to_value.onkeydown = function (e) {
            if (Utils.keydown(e)) {
                return e.preventDefault();
            }
            if (e.keyCode === 13) {
                _this.jump_to();
            }
        };
        return _this;
    }
    JumpControl.prototype.jump_to = function () {
        if (this.jump_value_isInvalid()) {
            return;
        }
        this.video.pause();
        if (this.um.um_get() === 'frames') {
            this.frame_goto(this.element.jump_to_value.value);
        }
        else {
            this.time_goto(this.element.jump_to_value.value);
        }
    };
    JumpControl.prototype.jump_value_isInvalid = function () {
        return isNaN(this.element.jump_to_value.value);
    };
    JumpControl.prototype.frame_goto = function (frame) {
        this.video.currentTime = Utils.frameToTime(frame, this.frameLength);
    };
    JumpControl.prototype.time_goto = function (time) {
        this.video.currentTime = time;
    };
    return JumpControl;
}(ControlloGenerico));
///<reference path="ControlloGenerico.ts"/>
var Markers = /** @class */ (function (_super) {
    __extends(Markers, _super);
    function Markers(conf) {
        var _this = _super.call(this, conf) || this;
        _this.markers_interval = null;
        _this.markers_timeout = 100;
        _this.time_mark = '00:00:00';
        _this.frame_mark = '000000';
        _this.smpte_mark = '00:00:00:00';
        _this.float_mark = '0.0000';
        _this.element.time_mark.innerHTML = _this.time_mark;
        _this.element.frame_mark.innerHTML = _this.frame_mark;
        _this.element.smpte_mark.innerHTML = _this.smpte_mark;
        _this.element.float_mark.innerHTML = _this.float_mark;
        return _this;
    }
    Markers.prototype.onplay = function () {
        var _this = this;
        this.markers_interval = setInterval(function () {
            if (_this.video.paused) {
                return;
            }
            _this.markers_update();
        }, this.markers_timeout);
    };
    Markers.prototype.onpause = function () {
        clearInterval(this.markers_interval);
    };
    Markers.prototype.ontimeupdate = function () {
        this.markers_update();
    };
    Markers.prototype.markers_update = function () {
        if (this.element.smpte_mark) {
            this.element.smpte_mark.innerText = this.format_time(true);
        }
        if (this.element.frame_mark) {
            this.element.frame_mark.innerText = Utils.Pad(Utils.currentFrame(this.video.currentTime, this.frameLength), 6);
        }
        if (this.element.time_mark) {
            this.element.time_mark.innerText = this.format_time(false);
        }
        if (this.element.float_mark) {
            this.element.float_mark.innerText = Markers.float_time(this.video.currentTime);
        }
    };
    /**
     * formatta il tempo eventualmente in formato SMTPE
     * @param {boolean} smpte
     * @returns {string}
     */
    Markers.prototype.format_time = function (smpte) {
        if (smpte === void 0) { smpte = true; }
        var time = this.video.currentTime;
        var hours = Utils.Floor((time / 3600), 0) % 24;
        var minutes = Utils.Floor((time / 60), 0) % 60;
        var seconds = Utils.Floor((time % 60), 0);
        var frames = Utils.Floor((((time % 1) * this.fps).toFixed(3)), 0);
        return (hours < 10 ? "0" + hours : hours) + ":"
            + (minutes < 10 ? "0" + minutes : minutes) + ":"
            + (seconds < 10 ? "0" + seconds : seconds)
            + (smpte ? ":" + (frames < 10 ? "0" + frames : frames) : '');
    };
    /**
     * formatta il tempo in secondi
     * @param time
     * @returns {number}
     */
    Markers.float_time = function (time) {
        return Utils.Round(time, 10).toFixed(4);
    };
    return Markers;
}(ControlloGenerico));
///<reference path="ControlloGenerico.ts"/>
var PlayButton = /** @class */ (function (_super) {
    __extends(PlayButton, _super);
    function PlayButton(conf) {
        var _this = _super.call(this, conf) || this;
        _this.ICO_PLAY = 0;
        _this.ICO_PAUSE = 1;
        _this.icons = _this.element.querySelectorAll('span');
        _this.element.onclick = function () {
            _this.play();
        };
        return _this;
    }
    PlayButton.prototype.play = function () {
        if (this.video.paused) {
            this.video.play();
        }
        else {
            this.video.pause();
        }
        this.showIcons();
    };
    PlayButton.prototype.showIcons = function () {
        var show = this.ICO_PLAY;
        var hide = this.ICO_PAUSE;
        if (this.video.paused) {
            show = this.ICO_PAUSE;
            hide = this.ICO_PLAY;
        }
        this.icons[show].classList.add('display-none');
        this.icons[hide].classList.remove('display-none');
    };
    PlayButton.prototype.onpause = function () {
        this.showIcons();
    };
    return PlayButton;
}(ControlloGenerico));
/**
 * Class ProgressBar
 * gestisce gli eventi sulla progress bar
 */
/// <reference path="ControlloGenerico.ts"/>
var ProgressBar = /** @class */ (function (_super) {
    __extends(ProgressBar, _super);
    function ProgressBar(conf) {
        var _this = _super.call(this, conf) || this;
        _this.step_set(_this.fps);
        //  Setto eventi oninput che onchange
        //  todo verifica supporto dei browser e inserisci condizione
        _this.element.oninput = function () {
            _this.progress_value();
        };
        _this.element.onchange = function () {
            _this.progress_value();
        };
        return _this;
    }
    ProgressBar.prototype.ontimeupdate = function () {
        this.element.value = this.video.currentTime / this.video.duration;
    };
    /**
     * Imposta lo step dello slider in relazione a durata del video e fps
     * @param fps
     */
    ProgressBar.prototype.step_set = function (fps) {
        this.element.step = 1 / (this.video.duration * fps);
    };
    /**
     * Evento per il cambio di valore della progressbar
     */
    ProgressBar.prototype.progress_value = function () {
        this.video.currentTime = this.video.duration * this.element.value;
    };
    return ProgressBar;
}(ControlloGenerico));
///<reference path="ControlloGenerico.ts"/>
var RangeControl = /** @class */ (function (_super) {
    __extends(RangeControl, _super);
    function RangeControl(conf) {
        var _this = _super.call(this, conf) || this;
        _this.um = conf.um || 'frames';
        _this.play_range = conf.play_range;
        _this.element.play_from.onkeydown = function (e) {
            if (Utils.keydown(e)) {
                return e.preventDefault();
            }
        };
        _this.element.play_from.onkeyup = function (e) {
            if (parseInt(_this.element.play_to.value) < parseInt(_this.element.play_from.value)) {
                _this.element.play_to.value = _this.element.play_from.value;
            }
            if (e.keyCode === 13) {
                _this.video.currentTime = _this.currentTime_set(_this.element.play_from.value);
            }
        };
        _this.element.play_to.onkeydown = function (e) {
            if (Utils.keydown(e)) {
                return e.preventDefault();
            }
            if (e.keyCode === 13) {
                _this.play();
            }
        };
        _this.element.play_int.onclick = function (e) {
            _this.play();
        };
        return _this;
    }
    RangeControl.prototype.play = function () {
        if (this.values_areInvalid()) {
            return;
        }
        var from = this.element.play_from.value;
        var to = this.element.play_to.value;
        if (this.um.um_get() === 'frames') {
            from = Utils.frameToTime(this.element.play_from.value, this.frameLength);
            to = Utils.frameToTime(this.element.play_to.value, this.frameLength);
        }
        // rimuovo opzione loop
        // this.play_range(from, to,  this.element.play_loop.checked);
        this.play_range(from, to, false);
    };
    RangeControl.prototype.values_areInvalid = function () {
        return isNaN(this.element.play_from.value) || isNaN(this.element.play_to.value) || parseInt(this.element.play_to.value) <= parseInt(this.element.play_from.value);
    };
    RangeControl.prototype.currentTime_set = function (v) {
        if (this.um.um_get() === 'frames') {
            return Utils.frameToTime(v, this.frameLength);
        }
        else {
            return v;
        }
    };
    return RangeControl;
}(ControlloGenerico));
///<reference path="ControlloGenerico.ts"/>
var SeekControl = /** @class */ (function (_super) {
    __extends(SeekControl, _super);
    function SeekControl(conf) {
        var _this = _super.call(this, conf) || this;
        _this.um = conf.um || 'frames';
        _this.element.backward.onclick = function () { _this.backward(); };
        _this.element.forward.onclick = function () { _this.forward(); };
        _this.element.step.onkeydown = function (e) {
            if (Utils.keydown(e)) {
                return e.preventDefault();
            }
            if (e.keyCode === 13) {
                _this.forward();
            }
        };
        return _this;
    }
    SeekControl.prototype.backward = function () {
        if (this.step_value_isInvalid()) {
            return;
        }
        this.video.pause();
        if (this.um.um_get() === 'frames') {
            this.frame_goto(Utils.currentFrame(this.video.currentTime, this.frameLength) - 1 * this.element.step.value);
        }
        else {
            this.time_goto(this.video.currentTime - 1 * this.element.step.value);
        }
    };
    SeekControl.prototype.forward = function () {
        if (this.step_value_isInvalid()) {
            return;
        }
        this.video.pause();
        if (this.um.um_get() === 'frames') {
            this.frame_goto(Utils.currentFrame(this.video.currentTime, this.frameLength) + 1 * this.element.step.value);
        }
        else {
            this.time_goto(this.video.currentTime + 1 * this.element.step.value);
        }
    };
    SeekControl.prototype.step_value_isInvalid = function () {
        return isNaN(this.element.step.value);
    };
    SeekControl.prototype.frame_goto = function (frame) {
        this.video.currentTime = Utils.frameToTime(frame, this.frameLength);
    };
    SeekControl.prototype.time_goto = function (time) {
        this.video.currentTime = time;
    };
    return SeekControl;
}(ControlloGenerico));
///<reference path="ControlloGenerico.ts"/>
var UMChange = /** @class */ (function (_super) {
    __extends(UMChange, _super);
    function UMChange(conf) {
        return _super.call(this, conf) || this;
    }
    UMChange.prototype.um_get = function () {
        return this.element ? this.element.value : 'frames';
    };
    return UMChange;
}(ControlloGenerico));
var Utils;
(function (Utils) {
    /**
     * Converte il tempo in frames
     * @param currentTime
     * @param frameLength
     * @returns {number}
     */
    function currentFrame(currentTime, frameLength) {
        return Math.ceil(currentTime / frameLength);
    }
    Utils.currentFrame = currentFrame;
    /**
     * Converte frame in tempo
     * @param frame
     * @param frameLength
     * @returns {number}
     */
    function frameToTime(frame, frameLength) {
        return frame * frameLength;
    }
    Utils.frameToTime = frameToTime;
    /**
     * Arrotondamento con precisione
     * @param Number
     * @param DecimalPlaces
     * @returns {number}
     */
    function Round(Number, DecimalPlaces) {
        return Math.round(parseFloat(Number) * Math.pow(10, DecimalPlaces)) / Math.pow(10, DecimalPlaces);
    }
    Utils.Round = Round;
    /**
     * Arrotondamento con precisione e decimali
     * @param Number
     * @param DecimalPlaces
     * @returns {string}
     * @constructor
     */
    function RoundFixed(Number, DecimalPlaces) {
        return Round(Number, DecimalPlaces).toFixed(DecimalPlaces);
    }
    Utils.RoundFixed = RoundFixed;
    /**
     * Arrotondamento inferiore
     * @param Number
     * @param DecimalPlaces
     * @returns {number}
     * @constructor
     */
    function Floor(Number, DecimalPlaces) {
        return Math.floor(parseFloat(Number) * Math.pow(10, DecimalPlaces)) / Math.pow(10, DecimalPlaces);
    }
    Utils.Floor = Floor;
    /**
     * Arrotondamento superiore
     * @param Number
     * @param DecimalPlaces
     * @returns {number}
     * @constructor
     */
    function Ceil(Number, DecimalPlaces) {
        return Math.ceil(parseFloat(Number) * Math.pow(10, DecimalPlaces)) / Math.pow(10, DecimalPlaces);
    }
    Utils.Ceil = Ceil;
    /**
     * Padding numero
     * @param Number
     * @param Length
     * @returns {string}
     * @constructor
     */
    function Pad(Number, Length) {
        var str = '' + Number;
        while (str.length < Length) {
            str = '0' + str;
        }
        return str;
    }
    Utils.Pad = Pad;
    function keydown(e, allowNegative) {
        if (allowNegative === void 0) { allowNegative = false; }
        var key = e.keyCode ? e.keyCode : e.which;
        //  todo in base alla lingua selezionare separatore decimale
        var comma = 188;
        var minus = 189;
        var period = 190;
        var valori = [
            8,
            9,
            13,
            27,
            46,
            110 //  decimal point
        ];
        if (allowNegative) {
            valori.push(minus);
        }
        valori.push(period); //  todo casomai in base alla lingua
        return (!(valori.indexOf(key) !== -1 ||
            (key == 65 && (e.ctrlKey || e.metaKey)) ||
            (key >= 35 && key <= 40) ||
            (key >= 48 && key <= 57 && !(e.shiftKey || e.altKey)) ||
            (key >= 96 && key <= 105)));
    }
    Utils.keydown = keydown;
})(Utils || (Utils = {}));
/**
 * Classe Controls
 * ---------------
 * Imposta gli eventi per i controlli
 */
var Controls = /** @class */ (function () {
    function Controls(conf) {
        //  Riferimento al video
        this.conf = null;
        this.video = null;
        //  Controlli
        this.wrapper = null;
        this.wrapperMarkers = null;
        this.wrapperElement = null;
        this.controls = {};
        this.hide_controls = {
            timeout: null,
            delay: 750
        };
        this.fast_play = null;
        this.conf = conf;
        this.video = conf.video;
        this.wrapperElement = conf.wrapper || '.controls__wrapper';
        //this.imposta();
    }
    Controls.prototype.imposta = function () {
        var _this = this;
        this.wrapper = document.querySelector(this.wrapperElement);
        this.wrapperMarkers = document.querySelector('.markers__wrapper');
        if (!this.wrapper) {
            return;
        }
        this.comandi_configura();
        //  Se hide_controls aggiungo eventi ai controlli ed al video
        if (this.conf.hide_controls && this.conf.hide_controls === true) {
            //  controlli
            this.wrapper.classList.add('controls__wrapper--autohide');
            this.wrapper.onmouseenter = function (e) { _this.onmouseenter(e); };
            this.wrapper.onmouseleave = function (e) { _this.onmouseleave(e); };
            this.wrapper.onfocus = function (e) { console.log("focus"); _this.onmouseenter(e); };
            //  video
            this.video.onmousemove = function (e) { _this.onmouseenter(e); };
            this.video.onmouseenter = function (e) { _this.onmouseenter(e); };
            this.video.onmouseout = function (e) { _this.onmouseleave(e); };
        }
        //  Markers
        this.conf.element = {
            smpte_mark: this.comando_get('smpte_mark'),
            frame_mark: this.comando_get('frame_mark'),
            time_mark: this.comando_get('time_mark'),
            float_mark: this.comando_get('float_mark')
        };
        this.comando_set('markers', new Markers(this.conf));
        //  Change FPS
        this.comando_set('fps', new FpsChange(this.conf_set('fps')));
        //  Progress Bar
        this.comando_set('progress', new ProgressBar(this.conf_set('progress')));
        //  Play Button
        this.comando_set('play', new PlayButton(this.conf_set('play')));
        //  GotoStart Button
        this.comando_set('goto_start', new GotoStartButton(this.conf_set('goto_start')));
        //  GotoEnd Button
        this.comando_set('goto_end', new GotoEndButton(this.conf_set('goto_end')));
        //  Change UM
        this.comando_set('um', new UMChange(this.conf_set('um')));
        //  Seek Control
        this.conf.element = {
            backward: this.comando_get('seek_backward'),
            step: this.comando_get('seek_step'),
            forward: this.comando_get('seek_forward')
        };
        this.conf.um = this.controls['um'].component;
        this.comando_set('seek', new SeekControl(this.conf));
        //  Jump Control
        this.conf.element = {
            jump_to: this.comando_get('jump_to'),
            jump_to_value: this.comando_get('jump_to_value')
        };
        this.conf.um = this.controls['um'].component;
        this.comando_set('jump', new JumpControl(this.conf));
        //  Range Control
        this.conf.element = {
            play_from: this.comando_get('play_from'),
            play_to: this.comando_get('play_to'),
            play_int: this.comando_get('play_int'),
            play_loop: this.comando_get('play_loop')
        };
        this.conf.um = this.controls['um'].component;
        //  Esporto metodo per stop automatico
        this.conf.play_range = this.conf.videoPlayer.play_range.bind(this.conf.videoPlayer);
        this.comando_set('range', new RangeControl(this.conf));
        //  Fast backward e forward
        this.conf.element = {
            backward: this.comando_get('backward'),
            forward: this.comando_get('forward')
        };
        this.comando_set('fast', new FastControl(this.conf));
        //  Fullscreen
        this.comando_set('fullscreen', new FullScreen(this.conf_set('fullscreen')));
        //  Volume
        this.comando_set('volume', new VolumeControl(this.conf_set('volume')));
        //  Switch Video
        this.comando_set('switch', new SwitchVideoControl(this.conf_set('switch')));
    };
    /**
     * Crea riferimenti al dom
     */
    Controls.prototype.comandi_configura = function () {
        //  Progress bar
        this.comando_registra('progress', '#range');
        //  Marker frame / tempo
        this.comando_registra('markers', null); // collettivo
        this.comando_registra('time_mark', '#time_mark');
        this.comando_registra('smpte_mark', '#smpte_mark');
        this.comando_registra('frame_mark', '#frame_mark');
        this.comando_registra('float_mark', '#float_mark');
        //  Inizio / Fine
        this.comando_registra('goto_start', '#goto_start');
        this.comando_registra('goto_end', '#goto_end');
        //  Play / pause
        this.comando_registra('play', '#play');
        //  Unit of measure
        this.comando_registra('um', '#controls_um');
        //  Rewind / Fastforward
        this.comando_registra('fast', null);
        this.comando_registra('backward', '#backward');
        this.comando_registra('forward', '#forward');
        //  Seek frame / tiem
        this.comando_registra('seek', null); // collettivo
        this.comando_registra('seek_backward', '#seek_backward');
        this.comando_registra('seek_forward', '#seek_forward');
        this.comando_registra('seek_step', '#seek_step');
        //  Jump to frame / time
        this.comando_registra('jump', null); // collettivo
        this.comando_registra('jump_to', '#jump_to');
        this.comando_registra('jump_to_value', '#jump_to_value');
        //  Play interval
        this.comando_registra('range', null); // collettivo
        this.comando_registra('play_from', '#play_from');
        this.comando_registra('play_to', '#play_to');
        this.comando_registra('play_int', '#play_int');
        this.comando_registra('play_loop', '#play_loop');
        //  Set Frame rate
        this.comando_registra('fps', '#fps');
        //  Fullscreen
        this.comando_registra('fullscreen', '#fullscreen');
        //   Volume
        this.comando_registra('volume', '#volume');
        //  SwitchVideo
        this.comando_registra('switch', '#switch_video_format');
    };
    Controls.prototype.conf_set = function (elemento) {
        this.conf.element = this.comando_get(elemento);
        return this.conf;
    };
    Controls.prototype.comando_registra = function (nome, selector) {
        this.controls[nome] = {
            selector: selector,
            ref: nome.indexOf('_mark') === -1 ? this.wrapper.querySelector(selector) : this.wrapperMarkers.querySelector(selector),
            component: null
        };
    };
    Controls.prototype.comando_get = function (nome) {
        return this.controls[nome].ref;
    };
    Controls.prototype.comando_set = function (nome, component) {
        this.controls[nome].component = component;
    };
    //  Eventi per autohide
    Controls.prototype.onmouseenter = function (e) {
        this.wrapper.classList.add('controls__wrapper--visible');
        clearTimeout(this.hide_controls.timeout);
    };
    Controls.prototype.onmouseleave = function (e) {
        var _this = this;
        clearTimeout(this.hide_controls.timeout);
        this.wrapper.classList.add('controls__wrapper--visible');
        this.hide_controls.timeout = setTimeout(function () {
            _this.wrapper.classList.remove('controls__wrapper--visible');
        }, this.hide_controls.delay);
    };
    /**
     * Cicla i compomenti richiamando il metodo corrispondente all'evento event
     * @param event
     */
    Controls.prototype.emit = function (event) {
        for (var key in this.controls) {
            if (this.controls.hasOwnProperty(key)) {
                var value = this.controls[key];
                if (value.component) {
                    value.component[event]();
                }
            }
        }
    };
    return Controls;
}());
/**
 * Spinner da visualizzare quando il video va in pausa
 */
var VideoSpinner = /** @class */ (function () {
    function VideoSpinner(conf) {
        this.conf = null;
        this.mask = null;
        this.timeout = null;
        this.delay = 300;
        this.conf = conf;
    }
    VideoSpinner.prototype.show = function () {
        var _this = this;
        this.timeout = setTimeout(function () {
            if (_this.timeout !== null) {
                //console.log(this.timeout, "timeout cleared intrnally");
                _this.hide();
            }
            _this.mask.classList.add('video_mask--active');
        }, this.delay);
        //console.log(this.timeout, "set timeout");
    };
    VideoSpinner.prototype.hide = function () {
        this.clearInterval();
        this.mask.classList.remove('video_mask--active');
    };
    VideoSpinner.prototype.clearInterval = function () {
        //console.log(this.timeout, "clearing timeout");
        clearInterval(this.timeout);
        this.timeout = null;
    };
    VideoSpinner.prototype.create = function () {
        this.mask = document.createElement('div');
        this.mask.className = 'video_mask';
        var spinner = document.createElement('div');
        spinner.className = 'spinner';
        VideoSpinner.template_default(spinner);
        this.mask.appendChild(spinner);
        return this.mask;
    };
    VideoSpinner.prototype.update = function (video) {
        var v = video.getBoundingClientRect();
        this.mask.style.width = v.width + 'px';
        this.mask.style.height = v.height + 'px';
    };
    VideoSpinner.template_default = function (spinner) {
        for (var i = 0; i < 5; i++) {
            var rect = document.createElement('div');
            rect.className = "rect" + (i + 1);
            spinner.appendChild(rect);
        }
    };
    return VideoSpinner;
}());
///<reference path="ControlloGenerico.ts"/>
var SwitchVideoControl = /** @class */ (function (_super) {
    __extends(SwitchVideoControl, _super);
    function SwitchVideoControl(conf) {
        var _this = _super.call(this, conf) || this;
        _this.src_current = {
            path: null,
            search: null
        };
        _this.source = _this.video.querySelector('source');
        _this.options = Array.prototype.slice.call(_this.element.querySelectorAll('option'));
        _this.src_current = _this.src_parse(_this.source_get());
        _this.source_set_initial();
        _this.element.onchange = function (e) { _this.source_set(e); };
        return _this;
    }
    SwitchVideoControl.prototype.source_set_initial = function () {
        var detected_type = this.src_current.search.type || 'video';
        this.options.filter(function (o) { return o.value === detected_type; })[0].selected = true;
    };
    SwitchVideoControl.prototype.source_get = function () {
        return this.source.src;
    };
    SwitchVideoControl.prototype.source_set = function (e) {
        this.video.pause();
        this.src_current.search.type = this.element.value || 'video';
        this.source.src = this.src_current.path + "?" + this.src_pars_encode(this.src_current.search);
        this.video.currentTime = 0;
        this.video.load();
    };
    SwitchVideoControl.prototype.src_parse = function (source) {
        var a = document.createElement('a');
        a.href = source;
        return {
            path: a.protocol + "//" + a.host + a.pathname,
            search: this.src_pars_decode(a.search.substring(1))
        };
    };
    SwitchVideoControl.prototype.src_pars_encode = function (search) {
        return Object.keys(search).map(function (k) { return k + "=" + search[k]; }).join('&');
    };
    SwitchVideoControl.prototype.src_pars_decode = function (search) {
        if (!search) {
            return { type: 'video' };
        }
        return JSON.parse('{"' + search.replace(/&/g, '","').replace(/=/g, '":"') + '"}', function (key, value) { return key === "" ? value : decodeURIComponent(value); });
    };
    return SwitchVideoControl;
}(ControlloGenerico));
///<reference path="ControlloGenerico.ts"/>
var VolumeControl = /** @class */ (function (_super) {
    __extends(VolumeControl, _super);
    function VolumeControl(conf) {
        var _this = _super.call(this, conf) || this;
        _this.ico_off = null;
        _this.ico_down = null;
        _this.ico_up = null;
        _this.ico_volume_up = null;
        _this.ico_volume_down = null;
        _this.volume_info = null;
        _this.volume_last_value = 0;
        //  Icone
        var icone = _this.element.querySelectorAll('.volume__icon');
        _this.ico_off = icone[0];
        _this.ico_down = icone[1];
        _this.ico_up = icone[2];
        //  Clic sulle icone
        _this.ico_off.onclick = function () {
            _this.volume_unmute();
        };
        _this.ico_down.onclick = function () {
            _this.volume_mute();
        };
        _this.ico_up.onclick = function () {
            _this.volume_mute();
        };
        //  Pulsanti
        _this.ico_volume_up = _this.element.querySelector('.volume__up');
        _this.ico_volume_down = _this.element.querySelector('.volume__down');
        _this.ico_volume_up.onclick = function () {
            _this.volume_set(0.1);
        };
        _this.ico_volume_down.onclick = function () {
            _this.volume_set(-0.1);
        };
        //  Info
        _this.volume_info = _this.element.querySelector('.volume_info');
        _this.interface();
        return _this;
    }
    VolumeControl.prototype.volume_set = function (v) {
        var volume_new = this.video.volume + v;
        if (volume_new > 1 || volume_new < 0) {
            return;
        }
        if (volume_new === 1) {
            //  nascondo +
        }
        else if (volume_new === 0) {
            //  nascondo -
        }
        else {
            // mostro tutto
        }
        this.video.volume = volume_new;
    };
    VolumeControl.prototype.volume_mute = function () {
        this.volume_last_value = this.video.volume;
        this.video.volume = 0;
    };
    VolumeControl.prototype.volume_unmute = function () {
        this.video.volume = this.volume_last_value;
    };
    VolumeControl.prototype.interface = function () {
        if (this.video.volume < 0.1) {
            this.icon_display(this.ico_off);
            this.ico_volume_hide(this.ico_volume_down);
            this.volume_info.innerHTML = '0.0';
        }
        else if (this.video.volume > 0.9) {
            this.icon_display(this.ico_up);
            this.ico_volume_hide(this.ico_volume_up);
            this.volume_info.innerHTML = '1.0';
        }
        else if (this.video.volume > 0.7) {
            this.icon_display(this.ico_up);
            this.volume_info.innerHTML = this.video.volume.toFixed(1);
        }
        else {
            this.icon_display(this.ico_down);
            this.ico_volume_hide(null);
            this.volume_info.innerHTML = this.video.volume.toFixed(1);
        }
    };
    VolumeControl.prototype.ico_volume_hide = function (icon) {
        this.ico_volume_up.classList.remove('visibility-hidden');
        this.ico_volume_down.classList.remove('visibility-hidden');
        if (icon) {
            icon.classList.add('visibility-hidden');
        }
    };
    VolumeControl.prototype.icon_display = function (icon) {
        this.ico_off.classList.add('display-none');
        this.ico_down.classList.add('display-none');
        this.ico_up.classList.add('display-none');
        icon.classList.remove('display-none');
    };
    VolumeControl.prototype.onvolumechange = function () {
        this.interface();
    };
    return VolumeControl;
}(ControlloGenerico));
/**
 *  Oggetto per il render delle scene sulla Seekbar
 */
var Scenes = /** @class */ (function () {
    function Scenes(conf, parent) {
        this.conf = null;
        this.parent = null;
        this.scene = [];
        this.video = null;
        this.click = function (classe, e) {
            //  setto stop automatico a fine scena se è premuto il tasto ctrl
            classe.parent.video.scena_set(this, e.ctrlKey);
        };
        this.conf = conf;
        this.scene = conf.scene;
        this.video = conf.video;
        this.parent = parent;
    }
    Scenes.prototype.add = function (scena) {
        this.scene.push(scena);
    };
    //  Inserisce una scena
    Scenes.prototype.render = function (scena) {
        var scene = document.createElement('div');
        scene.className = 'scena noselect';
        scene.onmousedown = function (e) {
            e.preventDefault();
        };
        this.set_styles(scene, scena);
        scene.innerHTML = "\n            <div class='fondino'></div>\n            <div class='nome noselect' title='" + scena.title + " - running time: " + (scena.end - scena.start).toFixed(2) + " sec.'>\n                " + scena.title + "<br>" + (scena.end - scena.start).toFixed(2) + "&nbsp;sec.\n            </div>";
        //  inizio
        var start_time = document.createElement('small');
        start_time.className = 'time start_time';
        start_time.innerHTML = '&#9658; ' + scena.start.toFixed(2);
        var end_time = document.createElement('small');
        end_time.className = 'time end_time';
        end_time.innerHTML = scena.end.toFixed(2) + ' &#9668;';
        scene.appendChild(start_time);
        scene.appendChild(end_time);
        scene.onclick = this.click.bind(scena, this);
        return scene;
    };
    Scenes.prototype.set_styles = function (el, scena) {
        el.style.backgroundImage = "url(" + scena.thumbnail + ")";
        el.style.left = scena.start * 100 / this.video.duration + "%";
        el.style.width = (scena.end - scena.start) * 100 / this.video.duration + "%";
    };
    Scenes.prototype.render_all = function (elementoACuiAggiungereLeScene) {
        var _this = this;
        this.scene.forEach(function (s) { return elementoACuiAggiungereLeScene.appendChild(_this.render(s)); });
    };
    return Scenes;
}());
/**
 * Crea la barra delle scene ed i suoi eventi
 */
var Seekbar = /** @class */ (function () {
    function Seekbar(conf, parent) {
        this.conf = null;
        this.parent = null;
        this.seek_bar = null;
        this.seek_bar_wrapper = null;
        this.seek_bar_inital_position = null;
        this.scene_wrapper = null;
        //  Gestione dimensione barra di scorrimento
        this.scene_wrapper_fattore = 2;
        this.scene_min_width = 0; // soglia in pixel sotto la quale viene ricalcolato scene_wrapper_fattore
        this.scene_current = null;
        this.SceneComponent = null;
        this.video = null;
        this.seek_bar_value = null;
        this.scene_translate = null;
        this.seek_bar_movement = null;
        this.frame_pixel = null;
        this.conf = conf;
        this.video = conf.video;
        this.parent = parent;
    }
    Seekbar.prototype.create = function () {
        this.seek_bar_wrapper = document.createElement('div');
        this.seek_bar_wrapper.className = 'seek_bar_wrapper';
        this.seek_bar = document.createElement('div');
        this.seek_bar.className = 'seek_bar';
        this.scene_wrapper = document.createElement('div');
        this.scene_wrapper.onmousedown = function (e) {
            e.preventDefault();
        };
        this.scene_wrapper.appendChild(this.seek_bar);
        this.scene_wrapper.className = 'scene_wrapper';
        this.scene_wrapper.style.width = (this.scene_wrapper_fattore) * 100 + "%";
        //  appendo al contenitore
        this.seek_bar_wrapper.appendChild(this.scene_wrapper);
        //  eventi
        // this.seek_bar_wrapper.onmousedown = this.seek.bind(this.seek_bar_wrapper, this);
        //this.seek_bar_wrapper.onmousedown = this.dragMouseDown.bind(this.seek_bar_wrapper, this);
        return this.seek_bar_wrapper;
    };
    ////    Drag test
    Seekbar.prototype.dragMouseDown = function (classe, e) {
        e = e || window.event;
        classe.seek_bar_inital_position = e.clientX; //-  classe.seek_bar_wrapper.getBoundingClientRect().left;
        document.onmouseup = classe.mouseUp.bind(this.seek_bar_wrapper, classe);
        document.onmousemove = classe.mouseMove.bind(this.seek_bar_wrapper, classe);
    };
    Seekbar.prototype.mouseUp = function (classe, e) {
        document.onmouseup = null;
        document.onmousemove = null;
    };
    Seekbar.prototype.mouseMove = function (classe, e) {
        if (e.clientX - classe.seek_bar_inital_position === 0) {
            return;
        }
        var move = (e.clientX - classe.seek_bar_wrapper.getBoundingClientRect().left);
        if (move < 0) {
            move = 0;
        }
        classe.seek_bar.style.left = move + 'px';
    };
    Seekbar.prototype.showScenes = function (scene, video_duration) {
        var _this = this;
        scene.forEach(function (s) {
            var pixel = (_this.seek_bar_wrapper.clientWidth / 100 * ((s.end - s.start) / video_duration * 100)) * _this.scene_wrapper_fattore;
            if (pixel < _this.scene_min_width) {
                var t = (_this.scene_wrapper_fattore * _this.scene_min_width) / pixel;
                _this.scene_wrapper_fattore = (_this.scene_wrapper_fattore * _this.scene_min_width) / pixel;
            }
        });
        this.SceneComponent = new Scenes({ scene: scene, video: this.video }, { seekbar: this, video: this.parent });
        this.scene_wrapper.style.width = (this.scene_wrapper_fattore) * 100 + "%";
        this.SceneComponent.render_all(this.scene_wrapper);
        //  Timer per determinare la scena corrente
        setInterval(function () {
            if (_this.video.paused) {
                return;
            }
            var _scene = document.querySelectorAll('.scena');
            for (var s = 0; s < scene.length; s++) {
                scene[s].active = false;
                // console.log("this.video.currentTime",  this.video.currentTime);
                // console.log("scene[s].start",  scene[s].start);
                // console.log("scene[s].end",  scene[s].end);
                if (_this.video.currentTime >= scene[s].start && _this.video.currentTime <= scene[s].end) {
                    if (_this.scene_current !== s) {
                        _this.scene_current = s;
                        scene[s].active = true;
                        _scene.forEach(function (s) { return s.classList.remove('scena--running'); });
                        _scene[s].classList.add('scena--running');
                    }
                }
            }
        }, 100);
    };
    Seekbar.prototype.seek = function (classe, e) {
        //  Se è stato premuto un tasto diverso dal sinistro, esco
        if (e.which && e.which !== 1) {
            return;
        }
        //  Se è premuto il tasto ctrl non faccio nulla ed attendo l'evento sulla scena
        if (e.ctrlKey) {
            return;
        }
        classe.move.call(this, classe, e);
        classe.seek_bar_wrapper.onmousemove = classe.move.bind(this, classe);
        var remove_event = classe.remove_events.bind(this, classe);
        classe.seek_bar_wrapper.onmouseup = remove_event;
        classe.seek_bar_wrapper.onmouseleave = remove_event;
    };
    Seekbar.prototype.run_animation = function () {
        var _this = this;
        this.frame_pixel = this.frame_pixel || this.scene_wrapper.getBoundingClientRect().width / (this.video.duration * this.conf.fps);
        this.seek_bar_interval = setInterval(function () {
            _this.set_value(100 / _this.video.duration * _this.video.currentTime);
        }, 100);
    };
    Seekbar.prototype.stop_animation = function () {
        clearInterval(this.seek_bar_interval);
    };
    Seekbar.prototype.set_value = function (val) {
        //  TODO totalmente ad minchiam, poi la mettiamo a posto?
        // -2 = dimensione barra
        //  todo collega a dimensioni dell'elemento
        var larghezzaBarra = 2;
        if (val !== this.seek_bar_value) {
            var sw = this.scene_wrapper.offsetWidth / 100 * val;
            var offset = this.scene_wrapper.offsetWidth / (this.scene_wrapper_fattore * 2);
            this.seek_bar_movement = val - this.seek_bar_value;
            this.seek_bar_value = val;
            //  sposto scene
            if (sw >= offset) {
                if (sw < this.scene_wrapper.offsetWidth - offset) {
                    this.scene_translate = sw - offset;
                    this.scene_wrapper.style.transform = "translateX(-" + this.scene_translate + "px)";
                }
                else {
                    this.scene_translate = this.scene_wrapper.offsetWidth - this.seek_bar_wrapper.offsetWidth + larghezzaBarra;
                    this.scene_wrapper.style.transform = "translateX(-" + this.scene_translate + "px)";
                }
            }
            else {
                /*//  console.log("B", val);
                                if (val === 0) {
                //                    console.log("B1");*/
                this.scene_translate = 0;
                this.scene_wrapper.style.transform = "translateX(-" + this.scene_translate + "px)";
                /*                } else {
                //                    console.log("B2");
                                    this.scene_translate = 0;
                                    this.scene_wrapper.style.transform = `translateX(-${this.scene_translate}px)`;
                                }*/
            }
            //  sposto barra
            //  ???
            if (this.frame_pixel * Math.ceil(this.video.currentTime / this.conf.frameLength) < this.scene_wrapper.offsetWidth) {
                this.seek_bar.style.transform = "translateX(" + this.frame_pixel * Math.ceil(this.video.currentTime / this.conf.frameLength) + "px)";
            }
            else {
                //  Ma siamo sicuri che serva togliere la larghezzaBarra
                this.seek_bar.style.transform = "translateX(" + (this.scene_wrapper.offsetWidth - larghezzaBarra) + "px)";
            }
        }
    };
    Seekbar.prototype.move = function (classe, e) {
        var perc = 0;
        var wrapper = classe.seek_bar_wrapper.getBoundingClientRect();
        //  Posizione del click all'interno dell'elemento
        var clickX = e.pageX - classe.seek_bar_wrapper.getBoundingClientRect().x;
        var clickS = (clickX + classe.scene_translate) * 100 / classe.scene_wrapper.offsetWidth;
        classe.video.currentTime = classe.video.duration * clickS / 100;
    };
    Seekbar.prototype.remove_events = function (classe) {
        classe.seek_bar_icon(classe.seek_bar_wrapper, false);
        classe.seek_bar_wrapper.onmousemove = null;
        classe.seek_bar_wrapper.onmouseup = null;
    };
    Seekbar.prototype.seek_bar_icon = function (element, set) {
        if (set === true) {
            this.seek_bar_wrapper.classList.add('dragging');
        }
        else {
            this.seek_bar_wrapper.classList.remove('dragging');
        }
    };
    return Seekbar;
}());
///<reference path="ControlloGenerico.ts"/>
var FastControl = /** @class */ (function (_super) {
    __extends(FastControl, _super);
    function FastControl(conf) {
        var _this = _super.call(this, conf) || this;
        _this.backward_interval = null;
        _this.forward_interval = null;
        _this.current = null;
        _this.fast_timeout = 100;
        _this.element.backward.onclick = function (e) {
            _this.fast(-1);
        };
        _this.element.forward.onclick = function (e) {
            _this.fast(1);
        };
        return _this;
    }
    FastControl.prototype.fast = function (fattore) {
        var _this = this;
        this.video.pause();
        //  Se esiste un timeout lo fermo
        if (this.current !== null) {
            if (this.current !== fattore) {
                this.clearInterval(this.current);
            }
            else {
                this.clearInterval(fattore);
                return;
            }
        }
        //  Attivo
        if (fattore === -1) {
            this.backward_interval = setInterval(function () {
                if (_this.video.seeking) {
                    return;
                }
                _this.video.currentTime += fattore * .1;
            }, this.fast_timeout);
        }
        else {
            this.forward_interval = setInterval(function () {
                if (_this.video.seeking) {
                    return;
                }
                _this.video.currentTime += fattore * .1;
            }, this.fast_timeout);
        }
        this.current = fattore;
    };
    FastControl.prototype.clearInterval = function (current) {
        if (current === 1) {
            clearInterval(this.forward_interval);
            this.forward_interval = null;
        }
        else {
            clearInterval(this.backward_interval);
            this.backward_interval = null;
        }
        this.current = null;
    };
    FastControl.prototype.onplay = function () {
        this.clearInterval(1);
        this.clearInterval(-1);
    };
    FastControl.prototype.onbegin = function () {
        this.clearInterval(1);
        this.clearInterval(-1);
    };
    FastControl.prototype.onended = function () {
        this.clearInterval(1);
        this.clearInterval(-1);
    };
    return FastControl;
}(ControlloGenerico));
/**
 * Classe VideoPlayer
 * ------------------
 * Crea un player riproducendo il video specificato nella configurazione
 * Inserisce uno spinner per il caricamento
 * Binda i comandi al dom
 * Inserisce la barra a scorrimento delle scene
 */
var VideoPlayer = /** @class */ (function () {
    //  Andiamo!
    function VideoPlayer(conf) {
        //  Configurazione
        /**
         * {
         *      selector: classe o id dell'elemento in cui creare il video,
         *      sources: array di url,
         *      fps: intero,
         *      scene: oggetto contenente le scene,
         * }
         */
        this.conf = null;
        //  Configurazioni base del player
        this.default_player_conf = {
            controls: false,
            volume: 0.5
        };
        //  Contenitore del video
        this.video_container = null;
        //  Riferimento al video
        this.video = null;
        //  Controlli
        this.controls = null;
        this.hide_controls = {
            timeout: null,
            delay: 750
        };
        // private fast_play = null;
        //  fps reali del filmato
        this.fps = 0;
        //  fps impostati dal player
        this.current_fps = 0;
        //  "dimensione" del frame rispetto al tempo
        this.frameLength = 0;
        //  Tiene traccia del primo caricamento dei dati
        this.firstloadeddata = true;
        //  Interfaccia per autostop
        this.autostop = {
            active: false,
            loop: false,
            stopAt: null,
            startAt: null
        };
        //  Componenti esterni
        this.SpinnerComponent = null;
        this.SeekBarComponent = null;
        this.ControlsComponent = null;
        this.conf = conf;
        this.fps = conf.fps;
        this.current_fps = conf.fps;
        if (this.fps) {
            this.setFrameLength();
        }
        this.video_container = document.querySelector(conf.selector);
        this.video_container.className += ' video_container';
        this.video_create(conf.player);
        //  Componenti
        this.componenti_create();
        //  Seekbar
        this.seek_bar_create();
        //  Just in case
        //  un giorno potrà servire
        window.onresize = function (e) {
            console.log("resized");
        };
    }
    /**
     * Inizializza il componente per i controlli
     */
    VideoPlayer.prototype.componenti_create = function () {
        this.ControlsComponent = new Controls({
            videoPlayer: this,
            video: this.video,
            hide_controls: this.conf.hide_controls,
            fps: this.fps,
            frameLength: this.frameLength
        });
    };
    /**
     * Inserisce la seek bar se esiste l'oggetto SeekBar ed esistono scene
     */
    VideoPlayer.prototype.seek_bar_create = function () {
        if (window['Seekbar'] && this.conf.scene && this.conf.scene.length) {
            this.SeekBarComponent = new Seekbar({
                video: this.video,
                fps: this.fps,
                frameLength: this.frameLength
            }, this);
            this.video_container.appendChild(this.SeekBarComponent.create());
        }
    };
    //  Gestione player
    //  ---------------
    /**
     * Configura il player, binda gli eventi e lo inserisce nella pagina
     * @param conf
     */
    VideoPlayer.prototype.video_create = function (conf) {
        var _this = this;
        this.video = document.createElement('video');
        this.video.preload = "none";
        this.video.controls = false;
        this.video.volume = conf && (conf.volume !== undefined && conf.volume !== null) ? conf.volume : this.default_player_conf.volume;
        this.sources_add(this.conf.sources);
        //  Aggiungo video
        //  insertbefore così finisce sopra all'eventuale interfaccia
        var wrapper = document.querySelector('.video_wrapper');
        wrapper.insertBefore(this.video, wrapper.firstChild);
        this.video.load();
        // this.video_container.insertBefore(this.video, this.video_container.firstChild);
        //  Spinner
        //  Verifico che esista l'oggetto
        if (window['VideoSpinner']) {
            this.SpinnerComponent = new VideoSpinner({ target: this.conf.selector });
            wrapper.appendChild(this.SpinnerComponent.create());
        }
        //  Event bindings
        //  todo, vedi di usare le arrow function, almeno in ts
        this.video.onloadstart = function (e) {
            console.log("loadstart");
            _this.spinner_show();
        };
        this.video.onloadeddata = function (e) {
            console.log("loadeddata");
            if (_this.firstloadeddata) {
                //  Spinner
                _this.SpinnerComponent.update(_this.video);
                //  Controlli
                _this.ControlsComponent.imposta();
                //  Scene
                if (_this.conf.scene && _this.SeekBarComponent) {
                    _this.SeekBarComponent.showScenes(_this.conf.scene, _this.video.duration);
                }
                _this.video.currentTime = 0;
                _this.firstloadeddata = false;
            }
            _this.spinner_hide();
        };
        this.video.onplay = function (e) {
            _this.spinner_hide();
            if (_this.autostop.active && _this.autostop.loop && _this.autostop.startAt && _this.autostop.startAt) {
                console.log("we loop");
                _this.video.currentTime = _this.autostop.startAt;
            }
            // if (classe.ControlsComponent) {
            _this.ControlsComponent.emit('onplay');
            // }
            _this.seekbar_run_animation();
        };
        this.video.onpause = function (e) {
            _this.ControlsComponent.emit('onpause');
            _this.seekbar_stop_animation();
        };
        this.video.ontimeupdate = function (e) {
            //  stop automatico
            //  todo 0.250? per intercettare il prima possibile l'evento
            if (!_this.video.paused && _this.autostop.active && _this.autostop.stopAt && (_this.video.currentTime >= _this.autostop.stopAt - 0.250)) {
                if (_this.autostop.loop === false) {
                    _this.autostop.active = false;
                }
                _this.seekbar_stop_animation();
                _this.time_goto(_this.autostop.stopAt);
                return;
            }
            _this.ControlsComponent.emit('ontimeupdate');
            if (_this.video.currentTime == 0) {
                console.log("begin");
                _this.ControlsComponent.emit('onbegin');
            }
            _this.seekbar_run_animation();
        };
        this.video.onwaiting = function (e) {
            console.log("waiting");
            _this.spinner_show();
        };
        this.video.onplaying = function (e) {
            console.log("playing");
            _this.spinner_hide();
        };
        this.video.onseeking = function (e) {
            console.log("seeking");
            _this.spinner_show();
        };
        this.video.onseeked = function (e) {
            console.log("seeked");
            _this.spinner_hide();
        };
        this.video.oncanplaythrough = function () {
            //console.log("canplaythrough");
        };
        this.video.onclick = function (e) {
            _this.video.paused ? _this.video.play() : _this.video.pause();
        };
        this.video.onvolumechange = function (e) {
            _this.ControlsComponent.emit('onvolumechange');
        };
        this.video.onended = function (e) {
            _this.ControlsComponent.emit('onended');
        };
    };
    /**
     * Aggiunge sources
     * @param sources
     */
    VideoPlayer.prototype.sources_add = function (sources) {
        var _this = this;
        sources.forEach(function (s) {
            var source = document.createElement('source');
            source.src = s;
            _this.video.appendChild(source);
        });
    };
    /**
     * imposta una scena da riprodurre
     * @param scena
     * @param loop
     */
    VideoPlayer.prototype.scena_set = function (scena, loop) {
        //  riproduce una scena dall'inizio e si ferma alla fine
        this.autostop.active = true;
        this.autostop.stopAt = scena.end;
        this.autostop.startAt = scena.start;
        this.autostop.loop = loop;
        this.time_goto(scena.start);
    };
    /**
     * Imposta frameLength equivalente alla durata temporale di un frame
     */
    VideoPlayer.prototype.setFrameLength = function () {
        this.frameLength = 1 / this.fps;
    };
    /**
     * sposta il video al tempo passato
     * @param time
     */
    VideoPlayer.prototype.time_goto = function (time) {
        this.video.pause();
        this.video.currentTime = time;
        //  dipendente dal fps settato
        // this.video.currentTime = time * (this.current_fps / this.fps );
        //this.marks_update();
    };
    VideoPlayer.prototype.play_range = function (from, to, loop) {
        this.autostop.active = true;
        this.autostop.loop = loop;
        this.autostop.startAt = from;
        this.autostop.stopAt = to;
        this.video.currentTime = from;
        this.video.play();
    };
    //  Gestione spinner
    //  ----------------
    VideoPlayer.prototype.spinner_show = function () {
        if (this.SpinnerComponent) {
            this.SpinnerComponent.show();
        }
        // throw new Error('spinner show');
    };
    VideoPlayer.prototype.spinner_hide = function () {
        if (this.SpinnerComponent) {
            this.SpinnerComponent.hide();
        }
        // throw new Error('spinner hide');
    };
    //  Gestione seekbar
    //  ----------------
    VideoPlayer.prototype.seekbar_run_animation = function () {
        if (this.SeekBarComponent) {
            this.SeekBarComponent.run_animation();
        }
    };
    VideoPlayer.prototype.seekbar_stop_animation = function () {
        if (this.SeekBarComponent) {
            this.SeekBarComponent.stop_animation();
        }
    };
    return VideoPlayer;
}());
//# sourceMappingURL=VideoPlayer_bundle.js.map