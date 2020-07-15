import { AbstractControl, ValidatorFn } from "@angular/forms";

const isbn10Maybe = /^(?:[0-9]{9}X|[0-9]{10})$/,
  isbn13Maybe = /^(?:[0-9]{13})$/;

export function IsbnValidator(
  control: AbstractControl
): { [key: string]: any } {
  if (!control.value) {
    return null;
  }
  let sanitized = control.value.replace(/[\s-]+/g, ""),
    checksum = 0,
    i;
  if (sanitized.length === 10) {
    if (!isbn10Maybe.test(sanitized)) {
      return { isbn: true };
    }
    for (i = 0; i < 9; i++) {
      checksum += (i + 1) * sanitized.charAt(i);
    }
    if (sanitized.charAt(9) === "X") {
      checksum += 10 * 10;
    } else {
      checksum += 10 * sanitized.charAt(9);
    }
    if (checksum % 11 === 0) {
      return !!sanitized ? null : { isbn: true };
    }
  } else if (sanitized.length === 13) {
    if (!isbn13Maybe.test(sanitized)) {
      return { isbn: true };
    }
    var factor = [1, 3];
    for (i = 0; i < 12; i++) {
      checksum += factor[i % 2] * sanitized.charAt(i);
    }
    if (sanitized.charAt(12) - ((10 - (checksum % 10)) % 10) === 0) {
      return !!sanitized ? null : { isbn: true };
    }
  }
  return { isbn: true };
}
