import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
	name: 'secondsToTime'
})
export class SecondsToTimePipe implements PipeTransform {

	transform(input: string): string {
        let sec_num = parseInt(input, 10);
        if (isNaN(sec_num)) {
			return "n/a";
		}
	    let hours   = Math.floor(sec_num / 3600);
	    let minutes = Math.floor((sec_num - (hours * 3600)) / 60);
	    let seconds = sec_num - (hours * 3600) - (minutes * 60);
	    let hh = hours.toString();
	    let mm = minutes.toString();
	    let ss = seconds.toString();

	    if (hours   < 10) {hh   = "0"+hours;}
	    if (minutes < 10) {mm = "0"+minutes;}
	    if (seconds < 10) {ss = "0"+seconds;}
	    return (hours > 0) ? hh+':'+mm+':'+ss : mm+':'+ss;
	}

}