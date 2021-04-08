import { Injectable } from "@angular/core";
import { HttpClient } from "@angular/common/http";
import { AppLodService } from "./app-lod";
import { environment } from "@rapydo/../environments/environment";
import { Annotation, Vocabulary } from "../types";

enum Flag {
  Deselected = 0,
  Selected = 1,
}

@Injectable()
export class AppVocabularyService {
  vocabulary: Vocabulary = null;
  readonly lang = environment.CUSTOM.FRONTEND_LANG || "en";

  constructor(private http: HttpClient, private LodService: AppLodService) {}

  get(cb) {
    if (!cb || typeof cb !== "function") {
      console.error("AppVocabularyService", "Callback missing");
      return;
    }

    if (this.vocabulary) {
      cb(this.initVocabulary());
    } else {
      this.http
        .get<Vocabulary>("/app/custom/assets/vocabulary/vocabulary.json")
        .subscribe(
          (response) => {
            this.vocabulary = response;
            cb(this.initVocabulary());
          },
          (err) => {
            console.log("Vocabulary not found!", err);
          }
        );
    }
  }

  private initVocabulary() {
    this.vocabulary.terms.sort(this.sortByLabel).forEach((t) => {
      this.resetVocabulary(t);
    });
    return this.vocabulary;
  }

  private sortByLabel(a, b) {
    return a.label > b.label ? 1 : b.label > a.label ? -1 : 0;
  }

  private resetVocabulary(term) {
    term.open = false;
    if (term.hasOwnProperty("children")) {
      term.children.sort(this.sortByLabel).forEach((c) => {
        c.description =
          (term.description ? term.description + ", " : "") +
          (term.label[this.lang] || term.label["en"]);
        c.open = false;
        c.selected = false;
        this.resetVocabulary(c);
      });
    }
  }

  search(search_key, lang = "en") {
    let filter = [];

    let searchFn = (terms, searchKey) => {
      terms.forEach((t) => {
        if (t.hasOwnProperty("children")) {
          searchFn(t.children, searchKey);
        } else {
          let search_re = new RegExp(searchKey, "ig");
          if (search_re.test(t.label[lang])) {
            filter.push(this.annotation_create(t));
          }
        }
      });
    };

    searchFn(this.vocabulary.terms, search_key);
    return filter;
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
    this.vocabulary.terms.forEach((t) => {
      this.resetVocabulary(t);
    });
    return this.vocabulary;
  }

  select_term(term) {
    this.toggle_term(term, Flag.Selected);
  }

  deselect_term(term) {
    this.toggle_term(term, Flag.Deselected);
  }

  toggle_term(term, flag: Flag = null, node = null) {
    if (!node) {
      node = { children: this.vocabulary.terms };
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
