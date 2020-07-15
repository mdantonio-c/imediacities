/*
* .filter('nocomma', function() {
			return function(value) {
				return (!value) ? '' : value.replace(/,/g, '');
			};
		})
* */
import { Pipe, PipeTransform } from "@angular/core";

@Pipe({
  name: "nocomma",
})
export class NoCommaPipe implements PipeTransform {
  transform(value: any, ...args: any[]): any {
    return !value ? "" : value.replace(/,/g, "");
  }
}
