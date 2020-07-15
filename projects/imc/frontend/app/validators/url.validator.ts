import { AbstractControl, ValidatorFn } from "@angular/forms";

const url_pattern = new RegExp(
  "^https?:\\/\\/" + // protocol
  "(?:\\S+(?::\\S*)?@)?" + // authentication
  "((([a-z\\d]([a-z\\d-]*[a-z\\d])*)\\.)+[a-z]{2,}|" + // domain name
  "((\\d{1,3}\\.){3}\\d{1,3}))" + // OR ip (v4) address
    /*'(\\:\\d+)?(\\/[-a-z\\d%_.~+]*)*' + // port and path
	'(\\?[;&a-z\\d%_.~+=-]*)?' + // query string
	'(\\#[-a-z\\d_]*)?$' + // fragment locater*/
    "",
  "i"
);

export function UrlValidator(control: AbstractControl): { [key: string]: any } {
  if (!control.value) {
    return null;
  }
  return url_pattern.test(control.value) ? null : { url: true };
}
