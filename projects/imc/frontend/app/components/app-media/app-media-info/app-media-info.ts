import { Component, Input, OnInit } from "@angular/core";
import { AuthService } from "@rapydo/services/auth";
import { AppMediaService } from "../../../services/app-media";
import { is_item_owner } from "../../../decorators/app-item-owner";

// exclude description types: Scope, Documentation
const EXCLUDE_FROM_DESCRIPTIONS: string[] = ["08", "09"];

interface KeyDescriptionPair {
  key: string;
  description: string;
}

interface Description {
  description_type?: string;
  text: string;
  language?: KeyDescriptionPair;
}

@Component({
  selector: "app-media-info",
  templateUrl: "app-media-info.html",
})
export class AppMediaInfoComponent implements OnInit {
  @Input() info: any;
  @Input() user_language: any;

  @is_item_owner() is_item_owner;

  public isCollapsed = {
    title: true,
    description: false,
    scope: false,
    keyword: false,
    prod_information: true,
    coverage: false,
    copyright: false,
    owner: true,
    analogue: true,
    format: true,
  };
  item: any;
  descriptions: Description[] = [];
  scopes: Description[] = [];
  docs: Description[] = [];
  agents: { [key: string]: string[] };
  user: any;

  constructor(
    private AuthService: AuthService,
    private MediaService: AppMediaService
  ) {}

  expandCard(card) {
    this.isCollapsed[card] = !this.isCollapsed[card];
  }

  togglePublicAccess() {
    let newVal = !this.info._item[0].public_access;
    this.MediaService.updatePublicAccess(newVal);
  }

  printContainerInfo() {
    // from ffprobe in the following form: mov,mp4,m4a,3gp,3g2,mj2
    // as the item is always transcoded as mp4 look for mp4 in the list
    // or provide the first
    let containers = this.item.digital_format[0].split(",");
    return containers.includes("mp4") ? "mp4" : containers[0].trim();
  }

  printEncodingInfo() {
    // from ffprobe in the following long name form: H.264 / AVC / MPEG-4 AVC / MPEG-4 part 10
    // always print the first value
    const encoding = this.item.digital_format[1].split("/")[0].trim();
    return encoding === "None" ? "n/a" : encoding;
  }

  ngOnInit() {
    this.user = this.AuthService.getUser();
    if (this.info._descriptions) {
      // common descriptions
      this.descriptions = this.info._descriptions.filter(
        (d) =>
          !d.description_type ||
          !EXCLUDE_FROM_DESCRIPTIONS.includes(d.description_type.key)
      );

      // intention of creation
      this.scopes = this.info._descriptions.filter(
        (d) => d.description_type && d.description_type.key === "08"
      );

      // documentation
      this.docs = this.info._descriptions.filter(
        (d) => d.description_type && d.description_type.key === "09"
      );
    }
    if (this.info._item) {
      this.item = this.info._item[0]._other_version
        ? this.info._item[0]._other_version[0]
        : this.info._item[0];
    }
    if (this.info._contributors) {
      let aMap = {};
      aMap["Others"] = [];
      this.info._contributors.forEach((c) => {
        const name = c.names[0];
        if (!c.activities) {
          aMap["Others"].push(name);
        } else {
          c.activities.forEach((r) => {
            aMap[r] = aMap[r] || [];
            aMap[r].push(name);
          });
        }
      });
      this.agents = aMap;
    }
  }
}
