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
        //  Oggetti DOM
        this.dom = {
            controlli: {
                wrapper: '.controls__wrapper',
                progress: '#range',
                time_mark: '#time_mark',
                smpte_mark: '#smpte_mark',
                frame_mark: '#frame_mark',
                float_mark: '#float_mark',
                goto_start: '#goto_start',
                goto_end: '#goto_end',
                play: '#play',
                rewind: '#rewind',
                fastforward: '#fastforward',
                seek_step: '#seek_step',
                jump_to: '#jump_to',
                jump_to_value: '#jump_to_value',
                controls_um: '#controls_um',
                play_from: '#play_from',
                play_to: '#play_to',
                play_int: '#play_int',
                play_loop: '#play_loop',
                fps: '#fps'
            }
        };
        //  Controlli
        this.controls = null;
        this.video_controls = {
            progress: null,
            time_mark: null,
            smpte_mark: null,
            frame_mark: null,
            float_mark: null,
            goto_start: null,
            goto_end: null,
            play: null,
            rewind: null,
            fastforward: null,
            seek_step: null,
            jump_to: null,
            jump_to_value: null,
            controls_um: null,
            play_from: null,
            play_to: null,
            play_int: null,
            play_loop: null,
            fps: null
        };
        //  Marks
        this.time_mark = '00:00:00';
        this.frame_mark = '000000';
        this.smpte_mark = '00:00:00:00';
        this.float_mark = '0.0000';
        //  Riferimento al timer per aggiornamento marker
        this.marks_interval = null;
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
        //  Eventi player
        this.onwaiting = function (classe, e) {
            classe.spinner_show();
        };
        this.onplaying = function (classe, e) {
            classe.spinner_hide();
        };
        this.onseeked = function (classe, e) {
            classe.marks_update();
        };
        this.onplay = function (classe, e) {
            classe.spinner_hide();
            if (classe.autostop.active && classe.autostop.startAt && classe.autostop.startAt) {
                classe.video.currentTime = classe.autostop.startAt;
            }
            classe.seekbar_run_animation();
        };
        this.onpause = function (classe, e) {
            classe.seekbar_stop_animation();
        };
        /**
         * Evento per il play
         * @param classe parametro sul quale eseguo il bind di questa classe
         * @param e evento
         */
        this.play_click = function (classe, e) {
            //  todo asincronizza
            //  https://developers.google.com/web/updates/2017/06/play-request-was-interrupted
            var icons = this.querySelectorAll('span');
            if (classe.video.paused) {
                icons[0].classList.add('display-none');
                icons[1].classList.remove('display-none');
                classe.video.play();
            }
            else {
                icons[0].classList.remove('display-none');
                icons[1].classList.add('display-none');
                classe.video.pause();
            }
        };
        /**
         * Evento per lo spostamento della barra temporare
         * @param classe parametro sul quale eseguo il bind di questa classe
         * @param e evento
         */
        this.progress_click = function (classe, e) {
            if (e.which !== 1) {
                return;
            }
            var perc = e.offsetX * 100 / classe.video_controls.progress.offsetWidth;
            classe.video.currentTime = classe.video.duration * perc / 100;
        };
        this.conf = conf;
        this.fps = conf.fps;
        this.current_fps = conf.fps;
        if (this.fps) {
            this.setFrameLength();
        }
        this.video_container = document.querySelector(conf.selector);
        this.video_container.className += ' video_container';
        this.video_create(conf.player);
        //  Seekbar
        this.seek_bar_create();
        //  Just in case
        //  un giorno potrà servire
        window.onresize = function (e) {
            console.log("resized");
        };
    }
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
        this.video = document.createElement('video');

        this.video.controls = false;
        this.video.volume = conf && (conf.volume !== undefined && conf.volume !== null) ? conf.volume : this.default_player_conf.volume;
        this.sources_add(this.conf.sources);
        //  Aggiungo video
        //  insertbefore così finisce sopra all'eventuale interfaccia
        this.video_container.insertBefore(this.video, this.video_container.firstChild);
        //  Spinner
        //  Verifico che esista l'oggetto
        if (window['VideoSpinner']) {
            this.SpinnerComponent = new VideoSpinner({ target: this.conf.selector });
            this.video_container.appendChild(this.SpinnerComponent.create());
        }
        //  Event bindings
        //  todo, vedi di usare le arrow function, almeno in ts
        this.video.onloadstart = this.onloadstart.bind(this.video, this);
        this.video.onloadeddata = this.onloadeddata.bind(this.video, this);
        this.video.onplay = this.onplay.bind(this.video, this);
        this.video.onpause = this.onpause.bind(this.video, this);
        this.video.ontimeupdate = this.ontimeupdate.bind(this.video, this);
        this.video.onwaiting = this.onwaiting.bind(this.video, this);
        this.video.onplaying = this.onplaying.bind(this.video, this);
        this.video.onseeked = this.onseeked.bind(this.video, this);
        this.video.onclick = function (e) {
            this.paused ? this.play() : this.pause();
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
    VideoPlayer.prototype.onloadstart = function (classe, e) {
        classe.spinner_show();
    };
    VideoPlayer.prototype.onloadeddata = function (classe, e) {
        if (classe.firstloadeddata) {
            //  Controlli
            classe.set_The_Controls_For_The_Heart_Of_The_Sun();
            //  Scene
            if (classe.conf.scene && classe.SeekBarComponent) {
                classe.SeekBarComponent.showScenes(classe.conf.scene, classe.video.duration);
            }
            classe.video.currentTime = 0;
            classe.firstloadeddata = false;
        }
        classe.spinner_hide();
    };
    VideoPlayer.prototype.ontimeupdate = function (classe, e) {
        //  stop automatico
        //  todo 0.250? per intercettare il prima possibile l'evento
        if (!classe.video.paused && classe.autostop.active && classe.autostop.stopAt && (classe.video.currentTime >= classe.autostop.stopAt - 0.250)) {
            if (classe.autostop.loop === false) {
                classe.autostop.active = false;
            }
            classe.seekbar_stop_animation();
            classe.time_goto(classe.autostop.stopAt);
            return;
        }
        if (classe.video_controls.progress) {
            classe.video_controls.progress.value = classe.video.currentTime / classe.video.duration;
        }
        classe.seekbar_run_animation();
    };
    /**
     * imposta una scena da riprodurre
     * @param scena
     */
    //  forse non la uso più
    VideoPlayer.prototype.scena_set = function (scena) {
        //  riproduce una scena dall'inizio e si ferma alla fine
        //  todo molto grezzo, migliorare
        this.autostop.active = !this.autostop.active;
        if (this.autostop.active) {
            this.autostop.stopAt = scena.end;
            this.autostop.startAt = scena.start;
            this.autostop.loop = true;
            this.time_goto(scena.start);
        }
    };
    //  Gestione frames e tempo
    //  -----------------------
    /*
        //  Simulazione del tempo
        public get_fps_time () {
            return this.video.currentTime.toFixed(4);
            //  dipendente dal fps settato
            //return (this.video.currentTime / (this.current_fps / this.fps)).toFixed(4);
        }
    
        public get_fps_duration () {
            return this.video.duration.toFixed(4);
            //  dipendente dal fps settato
            // return (this.video.duration / (this.current_fps / this.fps)).toFixed(4);
        }
    
        public get_current_fps () {
            return this.current_fps;
        }*/
    /**
     * Imposta frameLength equivalente alla durata temporale di un frame
     */
    VideoPlayer.prototype.setFrameLength = function () {
        this.frameLength = 1 / this.fps;
    };
    /**
     * Determina il frame corrente in base al tempo del video
     * @returns {number}
     */
    VideoPlayer.prototype.currentFrame = function () {
        return Math.ceil(this.video.currentTime / this.frameLength);
    };
    /**
     * coverte frame in tempo
     * @param frame
     * @returns {number}
     */
    VideoPlayer.prototype.frameToTime = function (frame) {
        //  Staccare da frameLength e legare a current_fps, forse
        return frame * this.frameLength;
    };
    /**
     * sposta il video al tempo corrispondente ai frame passati
     * @param frame
     */
    VideoPlayer.prototype.frame_goto = function (frame) {
        this.video.pause();
        this.video.currentTime = this.frameToTime(frame);
        this.marks_update();
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
        this.marks_update();
    };
    /**
     * imposta velocità di riproduzione
     * @param speed
     */
    VideoPlayer.prototype.playbackRate = function (speed) {
        this.video.playbackRate = speed;
    };
    /**
     * imposta velocità di rirpoduzione in base al fps passato
     * @param fps
     */
    VideoPlayer.prototype.change_fps = function (fps) {
        this.current_fps = fps;
        this.playbackRate(this.current_fps / this.fps);
    };
    /**
     * riproduce l'intervallo from - to eventualmente in loop
     * @param from
     * @param to
     * @param um frames | seconds
     * @param loop boolean
     */
    VideoPlayer.prototype.play_interval = function (from, to, um, loop) {
        if (um === 'frames') {
            from = this.frameToTime(from);
            to = this.frameToTime(to);
        }
        this.autostop.active = true;
        this.autostop.loop = loop;
        this.autostop.startAt = from;
        this.autostop.stopAt = to;
        this.time_goto(from);
    };
    //  Gestione spinner
    //  ----------------
    VideoPlayer.prototype.spinner_show = function () {
        if (this.SpinnerComponent) {
            this.SpinnerComponent.show();
        }
    };
    VideoPlayer.prototype.spinner_hide = function () {
        if (this.SpinnerComponent) {
            this.SpinnerComponent.hide();
        }
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
    //  Gestione controlli
    //  ------------------
    /**
     * Cerca i comandi nel dom,
     * esegue il binding degli eventi
     */
    //  todo vedi di semplificare
    VideoPlayer.prototype.set_The_Controls_For_The_Heart_Of_The_Sun = function () {
        var _this = this;
        this.controls = document.querySelector(this.dom.controlli.wrapper);
        if (!this.controls) {
            return;
        }
        //  Cerco gli elementi del dom e li associo al relativo oggetto
        for (var _i = 0, _a = Object.entries(this.video_controls); _i < _a.length; _i++) {
            var _b = _a[_i], key = _b[0], value = _b[1];
            this.video_controls[key] = this.controls.querySelector(this.dom.controlli[key]);
        }
        //  Verifico quali oggetti sono bindati al dom ed associo gli eventi
        //  Barra temporale
        if (this.video_controls.progress) {
            this.video_controls.progress.step = 1 / (this.video.duration * this.fps);
            this.video_controls.progress.onclick = this.progress_click.bind(this.video_controls.progress, this);
            //this.video_controls.progress.oninput = this.progress_click.bind(this.video_controls.progress, this);
        }
        //  Se esistono i marker frame/temporali attivo un intervallo per gestire lo stato
        //  NB: non mi baso sull'evento timeupdate perchè non è affidabile e rende scattosa l'animazione
        if (this.marks_exists(null)) {
            this.marks_interval = setInterval(function () {
                if (_this.video.paused) {
                    return;
                }
                _this.marks_update();
            }, 100);
        }
        //  Pulsante play/pausa
        if (this.video_controls.play) {
            this.video_controls.play.onclick = this.play_click.bind(this.video_controls.play, this);
        }
        //  Pulsante vai all'inizio
        if (this.video_controls.goto_start) {
            this.video_controls.goto_start.onclick = function () { _this.time_goto(0); };
        }
        //  Pulsante vai alla fine
        if (this.video_controls.goto_end) {
            this.video_controls.goto_end.onclick = function () { _this.time_goto(_this.video.duration); };
        }
        //  Pulsante vai indietro
        if (this.video_controls.rewind) {
            this.video_controls.rewind.onclick = function () {
                if (isNaN(_this.video_controls.seek_step.value)) {
                    return;
                }
                if (_this.video_controls.controls_um.value === 'frames') {
                    _this.frame_goto(_this.currentFrame() - 1 * _this.video_controls.seek_step.value);
                }
                else {
                    _this.time_goto(_this.video.currentTime - 1 * _this.video_controls.seek_step.value);
                }
            };
        }
        //  Pulsante vai avanti
        if (this.video_controls.fastforward) {
            this.video_controls.fastforward.onclick = function () {
                if (isNaN(_this.video_controls.seek_step.value)) {
                    return;
                }
                if (_this.video_controls.controls_um.value === 'frames') {
                    _this.frame_goto(_this.currentFrame() + 1 * _this.video_controls.seek_step.value);
                }
                else {
                    _this.time_goto(_this.video.currentTime + 1 * _this.video_controls.seek_step.value);
                }
            };
        }
        //  Pulsante vai a
        if (this.video_controls.jump_to) {
            this.video_controls.jump_to.onclick = function () {
                if (isNaN(_this.video_controls.jump_to_value.value)) {
                    return;
                }
                if (_this.video_controls.controls_um.value === 'frames') {
                    _this.frame_goto(_this.video_controls.jump_to_value.value);
                }
                else {
                    _this.time_goto(_this.video_controls.jump_to_value.value);
                }
            };
        }
        //  Pulsante riproduci intervallo
        if (this.video_controls.play_int) {
            this.video_controls.play_int.onclick = function () {
                if (isNaN(_this.video_controls.play_from.value) || isNaN(_this.video_controls.play_to.value)) {
                    return;
                }
                _this.play_interval(_this.video_controls.play_from.value, _this.video_controls.play_to.value, _this.video_controls.controls_um.value, _this.video_controls.play_loop.checked);
            };
        }
        //  Cambio fps
        if (this.video_controls.fps) {
            this.video_controls.fps.onchange = function () {
                _this.change_fps(_this.video_controls.fps.value);
            };
        }
    };
    //  Gestione marker temporali
    //  -------------------------
    /**
     * Metodo di comondo per determinare se ci sono marker
     * @param mark
     * @returns {any}
     */
    VideoPlayer.prototype.marks_exists = function (mark) {
        if (mark) {
            return this.video_controls[mark];
        }
        else {
            return this.video_controls.time_mark || this.video_controls.frame_mark || this.video_controls.time_mark || this.video_controls.float_mark;
        }
    };
    /**
     * Metodo per l'aggiornamento dei marker
     */
    VideoPlayer.prototype.marks_update = function () {
        if (this.video_controls.smpte_mark) {
            this.video_controls.smpte_mark.innerText = this.format_time(true);
        }
        if (this.video_controls.frame_mark) {
            this.video_controls.frame_mark.innerText = VideoPlayer.Pad(this.currentFrame(), 6);
        }
        if (this.video_controls.time_mark) {
            this.video_controls.time_mark.innerText = this.format_time(false);
        }
        if (this.video_controls.float_mark) {
            this.video_controls.float_mark.innerText = VideoPlayer.float_time(this.video.currentTime);
        }
    };
    /**
     * formatta il tempo eventualmente in formato SMTPE
     * @param {boolean} smpte
     * @returns {string}
     */
    VideoPlayer.prototype.format_time = function (smpte) {
        if (smpte === void 0) { smpte = true; }
        var time = this.video.currentTime;
        var hours = VideoPlayer.Floor((time / 3600), 0) % 24;
        var minutes = VideoPlayer.Floor((time / 60), 0) % 60;
        var seconds = VideoPlayer.Floor((time % 60), 0);
        var frames = VideoPlayer.Floor((((time % 1) * this.fps).toFixed(3)), 0);
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
    VideoPlayer.float_time = function (time) {
        return VideoPlayer.Round(time, 10);
    };
    //  Arrotondamenti ed amenità varie
    VideoPlayer.Round = function (Number, DecimalPlaces) {
        return Math.round(parseFloat(Number) * Math.pow(10, DecimalPlaces)) / Math.pow(10, DecimalPlaces);
    };
    VideoPlayer.RoundFixed = function (Number, DecimalPlaces) {
        return VideoPlayer.Round(Number, DecimalPlaces).toFixed(DecimalPlaces);
    };
    VideoPlayer.Floor = function (Number, DecimalPlaces) {
        return Math.floor(parseFloat(Number) * Math.pow(10, DecimalPlaces)) / Math.pow(10, DecimalPlaces);
    };
    VideoPlayer.Ceil = function (Number, DecimalPlaces) {
        return Math.ceil(parseFloat(Number) * Math.pow(10, DecimalPlaces)) / Math.pow(10, DecimalPlaces);
    };
    VideoPlayer.Pad = function (Number, Length) {
        var str = '' + Number;
        while (str.length < Length) {
            str = '0' + str;
        }
        return str;
    };
    return VideoPlayer;
}());
//# sourceMappingURL=VideoPlayer.js.map