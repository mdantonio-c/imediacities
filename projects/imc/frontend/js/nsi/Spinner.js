/**
 * Spinner per caricamento
 */
var VideoSpinner = /** @class */ (function () {
    function VideoSpinner(conf) {
        this.conf = null;
        this.mask = null;
        this.conf = conf;
    }
    VideoSpinner.prototype.show = function () {
        this.mask.classList.add('video_mask--active');
    };
    VideoSpinner.prototype.hide = function () {
        this.mask.classList.remove('video_mask--active');
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
    VideoSpinner.template_default = function (spinner) {
        for (var i = 0; i < 5; i++) {
            var rect = document.createElement('div');
            rect.className = "rect" + (i + 1);
            spinner.appendChild(rect);
        }
    };
    return VideoSpinner;
}());
//# sourceMappingURL=Spinner.js.map