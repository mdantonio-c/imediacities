enum AppInfoDefaulMessages {
  success = "Operation completed successfully!",
  error = "Unable to complete the operation",
  info = "",
}

export function infoResult() {
  return function (target, key) {
    target[key] = new InfoResult();
    return target.key;
  };
}

class InfoResult {
  message = null;
  status = null;
  visible = false;

  show(status, message = "") {
    this.status = status;
    this.message = message || AppInfoDefaulMessages[status];
    this.visible = true;
  }

  hide() {
    this.visible = false;
  }
}
