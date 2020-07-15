enum AppInfoDefaulMessages {
  success = "Operation completed successfully!",
  error = "Unable to complete the operation",
  info = "",
}

export function infoResult() {
  return function (target, key) {
    target[key] = {
      message: null,
      status: null,
      visible: false,
      show: (status, message) => {
        show.bind(target[key])(status, message);
      },
      hide: () => {
        hide.bind(target[key])();
      },
    };
    return target.key;
  };
}

function show(status, message = "") {
  this.status = status;
  this.message = message || AppInfoDefaulMessages[status];
  this.visible = true;
}

function hide() {
  this.visible = false;
}
