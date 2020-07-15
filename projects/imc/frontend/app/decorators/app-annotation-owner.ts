export function is_annotation_owner() {
  return function (target, key) {
    target[key] = owns_annotation;
    return target.key;
  };
}

function owns_annotation(user, annotation_owner) {
  if (user == null) return false;
  return annotation_owner === user.uuid || user.isAdmin;
}
