import { Pipe, PipeTransform } from "@angular/core";

@Pipe({
  name: "duration",
})
export class DurationPipe implements PipeTransform {
  transform(input: string): string {
    let secs = parseInt(input, 10);
    if (isNaN(secs)) {
      return "n/a";
    }
    let cdate = new Date(0, 0, 0, 0, 0, secs);
    if (cdate.getHours() === 0 && cdate.getMinutes() > 0) {
      return cdate.getMinutes() + " min " + cdate.getSeconds() + " sec";
    } else if (cdate.getHours() === 0 && cdate.getMinutes() === 0) {
      return cdate.getSeconds() + " sec";
    } else {
      return (
        cdate.getHours() +
        " hour " +
        cdate.getMinutes() +
        " min " +
        cdate.getSeconds() +
        " sec"
      );
    }
  }
}
