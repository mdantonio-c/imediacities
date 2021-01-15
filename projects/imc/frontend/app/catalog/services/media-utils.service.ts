import { Injectable } from "@angular/core";
import { environment } from "@rapydo/../environments/environment";

export const LANG = environment.CUSTOM.FRONTEND_LANG || "en";

@Injectable()
export class MediaUtilsService {
  static getIdentifyingTitle(media: any, lang = LANG): string {
    let identifyingTitle: string;
    let entityType: string = media.type;
    if (entityType === "aventity") {
      // aventity: metadata comes with identitying_title
      identifyingTitle = media.identifying_title;
    } else {
      // nonaventity: first choice in the given lang (default english)
      for (let t of media._titles) {
        if (
          t.hasOwnProperty("language") &&
          t.language &&
          t.language.key === lang
        ) {
          identifyingTitle = t.text;
          break;
        }
      }
      // otherwise take the first on the list
      if (!identifyingTitle) {
        identifyingTitle = media._titles[0].text;
      }
    }
    return identifyingTitle;
  }

  static getDescription(media: any, lang = LANG): string {
    let description: string;
    let first: boolean = true;
    if (!media._descriptions) return null;
    for (let d of media._descriptions) {
      // take the first as default
      if (first) {
        first = !first;
        description = d.text;
      }
      if (
        d.hasOwnProperty("language") &&
        d.language &&
        d.language.key === lang
      ) {
        description = d.text;
        break;
      }
    }
    return description;
  }
}
