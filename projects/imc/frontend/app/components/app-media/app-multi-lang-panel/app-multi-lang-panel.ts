import {
  Input,
  Component,
  OnInit,
  AfterViewInit,
  ViewChild,
  ElementRef,
} from "@angular/core";

@Component({
  selector: "app-multi-lang-panel",
  templateUrl: "app-multi-lang-panel.html",
})
export class AppMultiLangPanelComponent implements OnInit, AfterViewInit {
  @Input() title: string = "n/a";
  @Input() data: any[];
  @Input() userLanguage: any;
  @Input() showType: boolean = false;
  @Input() typeAttr: string;
  @ViewChild("languages_selector", { static: false })
  languages_selector: ElementRef;

  isCollapsed: boolean = false;
  activeLang: string;
  languagesMap = new Map();

  ngOnInit(): void {
    if (this.userLanguage) {
      this.activeLang = this.userLanguage;
    }
    if (this.data) {
      this.getLanguages();
    }
  }

  ngAfterViewInit(): void {
    if (this.languagesMap.size > 1) {
      //  set events
      this.set_selector_events();
      // insert options for the language change select
      this.set_selector_options();
    }
  }

  expandCard() {
    this.isCollapsed = !this.isCollapsed;
  }

  /**
   * Create options for managing the language.
   * @private
   */
  private set_selector_options() {
    this.languagesMap.forEach((value, key, map) => {
      const option = document.createElement("option");
      option.innerText = value;
      option.value = key;
      option.selected = key === this.activeLang;

      this.languages_selector.nativeElement.appendChild(option);
    });
  }

  /**
   * Events for the management of the language change
   * @private
   */
  private set_selector_events() {
    // Stop event propagation so as not to cause the activation of the accordion by clicking
    // on the language selector
    this.languages_selector.nativeElement.onclick = function (e) {
      e.stopPropagation();
    };
    //  Event on language change
    this.languages_selector.nativeElement.onchange = () => {
      this.activeLang = this.languages_selector.nativeElement.value;
    };
  }

  /**
   * Loop descriptions in order to extract languages.
   * If the current language has not been set, it sets it to the first one
   * @private
   */
  private getLanguages() {
    let force_user_language = true;
    this.data.forEach((d) => {
      if (!d.language) {
        // for missing language
        this.languagesMap.set("n/a", "n/a");
        return;
      }
      if (!this.activeLang) {
        this.activeLang = d.language.key;
      }
      if (force_user_language && d.language.key === this.activeLang) {
        force_user_language = false;
      }
      this.languagesMap.set(d.language.key, d.language.description);
    });
    if (force_user_language) {
      let lang = this.data[0].language ? this.data[0].language.key : "n/a";
      this.activeLang = lang;
    }
  }
}
