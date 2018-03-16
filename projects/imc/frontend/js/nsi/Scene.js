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
            if (e.ctrlKey) {
                classe.parent.video.scena_set(this);
            }
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
        //this.scene_wrapper = this.SeekBarComponent.scene_wrapper;
        //this.scene_wrapper.appendChild(scene);
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
//# sourceMappingURL=Scene.js.map