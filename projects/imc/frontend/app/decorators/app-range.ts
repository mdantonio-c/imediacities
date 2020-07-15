export function rangePlayer() {
  return function (target, key) {
    target[key] = new _RangePlayer();
    return target.key;
  };
}

function _RangePlayer() {
  let _self = this;

  this._video = null;

  this._range = {
    active: false,
    duration: 0,
    check: function (currentTime) {
      return this.active && this.end && currentTime >= this.end;
    },
    end: null,
    index: 0,
    interval: null,
    loop: false,
    start: null,
    timer: 100,
  };

  this.set = (conf) => {
    this._video = conf.video;
    this.index = conf.index;
    this._range.start = (1 / this._video.fps) * conf.start;
    this._range.end = (1 / this._video.fps) * conf.end;

    this._range.loop = conf.loop;
    this._range.duration = this._range.end - this._range.start;

    this._range.active = true;

    if (this._range.interval) {
      this._unset();
    }

    if (this._range.loop) {
      this._video.player = {
        duration: +this._range.duration.toFixed(6),
        begin: +this._range.start.toFixed(6),
      };
    }
    this._video.video.pause();
    this._video.video.currentTime = this._range.start;
    this._video._emetti("onrange_start", this._range);

    this._range.interval = setInterval(() => {
      if (
        !this._video.video.paused &&
        this._range.check(this._video.video.currentTime)
      ) {
        this._video.video.pause();

        if (this._range.loop === false) {
          this._range.active = false;
        }

        if (this._range.loop) {
          this._video.restart_time = this._range.start;
        } else {
          this._unset();
        }

        //this._video.video.currentTime = this._range.start;
      }
    }, this._range.timer);
  };

  this.is_active = function () {
    return this._range.active;
  };

  this.get = function () {
    return this._range;
  };

  this._unset = function () {
    this._video._emetti("onrange_end", this._range);
    this._video.restart_time = null;
    clearInterval(this._range.interval);
    this._range.interval = null;
  };
}
