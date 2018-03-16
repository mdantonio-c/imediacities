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
        this.scene_min_width = 0;
        this.scene_wrapper_fattore = 2;
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
//# sourceMappingURL=Seekbar.js.map