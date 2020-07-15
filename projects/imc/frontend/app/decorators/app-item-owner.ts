export function is_item_owner() {
  return function (target, key) {
    target[key] = owns_item;
    return target.key;
  };
}

function owns_item(user, item) {
  return user.group["shortname"] === item._ownership[0].shortname;
}
