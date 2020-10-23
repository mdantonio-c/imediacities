import { Injectable } from "@angular/core";
import { HttpClient } from "@angular/common/http";
import { AppLodService } from "./app-lod";
import { environment } from "@rapydo/../environments/environment";
import { Annotation } from "../types";

enum Flag {
  Deselected = 0,
  Selected = 1,
}

@Injectable()
export class AppVocabularyService {
  _vocabolario = null;
  readonly lang = environment.CUSTOM.FRONTEND_LANG || "en";

  constructor(private http: HttpClient, private LodService: AppLodService) {}

  get(cb) {
    if (!cb || typeof cb !== "function") {
      console.error("AppVocabularyService", "Callback mancante");
      return;
    }

    if (this._vocabolario) {
      cb(this._vocabolario_init());
    } else {
      this.http.get("/app/custom/assets/vocabulary/vocabulary.json").subscribe(
        (response) => {
          this._vocabolario = response;
          cb(this._vocabolario_init());
        },
        (err) => {
          console.log("Vocabolario non trovato!", err);
        }
      );
    }
  }

  private _vocabolario_init() {
    this._vocabolario.terms.sort(this._sort_by_label).forEach((t) => {
      this._vocabolario_reset(t);
    });
    return this._vocabolario;
  }

  private _sort_by_label(a, b) {
    return a.label > b.label ? 1 : b.label > a.label ? -1 : 0;
  }

  private _vocabolario_reset(term) {
    term.open = false;
    if (term.hasOwnProperty("children")) {
      term.children.sort(this._sort_by_label).forEach((c) => {
        c.description =
          (term.description ? term.description + ", " : "") +
          (term.label[this.lang] || term.label["en"]);
        c.open = false;
        c.selected = false;
        this._vocabolario_reset(c);
      });
    }
  }

  search(search_key, lang = "en") {
    let filtro = [];

    let ricerca = (terms, search_key) => {
      terms.forEach((t) => {
        if (t.hasOwnProperty("children")) {
          ricerca(t.children, search_key);
        } else {
          let search_re = new RegExp(search_key, "ig");
          if (search_re.test(t.label[lang])) {
            filtro.push(this.annotation_create(t));
          }
        }
      });
    };

    ricerca(this._vocabolario.terms, search_key);
    return filtro;
  }

  annotation_create(term: Annotation, group = "term") {
    const label = term.label
      ? term.label[this.lang] || term.label["en"]
      : undefined;
    return {
      group: group,
      creator_type: "user",
      description: term.description,
      name: label || term.name,
      iri: term.id || term.iri || null,
      source: "vocabulary",
    };
  }

  reset() {
    this._vocabolario.terms.forEach((t) => {
      this._vocabolario_reset(t);
    });
    return this._vocabolario;
  }

  select_term(term) {
    this.toggle_term(term, Flag.Selected);
  }

  deselect_term(term) {
    this.toggle_term(term, Flag.Deselected);
  }

  toggle_term(term, flag: Flag = null, node = null) {
    if (!node) {
      node = { children: this._vocabolario.terms };
    }
    if (node.hasOwnProperty("children")) {
      node.children.forEach((c) => {
        this.toggle_term(term, flag, c);
      });
    } else {
      if (node.id === term.iri) {
        switch (flag) {
          case Flag.Selected:
            node.selected = true;
            break;
          case Flag.Deselected:
            node.selected = false;
            break;
          default:
            node.selected = !node.selected;
            break;
        }
      }
    }
  }
}
