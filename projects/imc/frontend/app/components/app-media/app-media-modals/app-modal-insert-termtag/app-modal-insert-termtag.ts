import {
  Component,
  ChangeDetectorRef,
  OnInit,
  OnChanges,
  Input,
  AfterViewInit,
  ViewChild,
  ElementRef,
  Output,
  EventEmitter,
} from "@angular/core";
import { AppVocabularyService } from "../../../../services/app-vocabulary";
import { AppAnnotationsService } from "../../../../services/app-annotations";
import { Subject } from "rxjs";
import { debounceTime, map } from "rxjs/operators";
import { HttpClient } from "@angular/common/http";
import { AppLodService } from "../../../../services/app-lod";
import { infoResult } from "../../../../decorators/app-info";
import { environment } from "@rapydo/../environments/environment";
import { Annotation } from "../../../../types";

@Component({
  selector: "app-modal-insert-termtag",
  templateUrl: "app-modal-insert-termtag.html",
})
export class AppModalInsertTermtagComponent
  implements OnInit, OnChanges, AfterViewInit {
  @Input() data: any;
  @Input() media_type: string;
  @ViewChild("p", { static: false }) p;

  @infoResult() save_result;
  @infoResult() add_tag;

  ricerca_model;
  results = {
    vocabulary: [],
    vocabulary_nav: {
      page_size: 10,
      page_start: 0,
      page_end: 10,
      hide_next: false,
      hide_prev: true,
    },
    lods: [],
    lods_nav: {
      page_size: 10,
      page_start: 0,
      page_end: 10,
      hide_next: false,
      hide_prev: true,
    },
    show: "v",
    key: "",
  };

  private subject: Subject<string> = new Subject();
  readonly lang = environment.CUSTOM.FRONTEND_LANG || "en";

  @ViewChild("search_field", { static: false }) search_field: ElementRef;

  @Output() shots_update: EventEmitter<any> = new EventEmitter();

  constructor(
    private http: HttpClient,
    private LodService: AppLodService,
    private vocabularyService: AppVocabularyService,
    private AnnotationsService: AppAnnotationsService,
    private ref: ChangeDetectorRef
  ) {}

  vocabolario = null;
  // vocabolario_visualizza = false;

  embargo_enable = false;
  embargo_model;

  ricerca_risultati = [];
  ricerca_key = {
    name: "",
  };
  ricerca_nomatch = false;

  terms: Annotation[] = [];
  terms_all = [];

  onKeyup(event) {
    this.subject.next(event);
  }

  /**
   * Search for the term in the dictionary and on wikidata
   * @param term
   * @returns {any}
   */
  search_vocabulary_and_lods(event) {
    const term = event.target.value;
    if (term.length < 2) return;

    if (this.results.key === term) {
      if (event.keyCode === 13) {
        this.p.open();
      }
      return;
    }

    this.results.key = term;
    this.add_tag.hide();

    //  resetto visualizzazione risultati
    this.results.vocabulary_nav = {
      page_size: 10,
      page_start: 0,
      page_end: 10,
      hide_next: false,
      hide_prev: true,
    };
    this.results.lods_nav = {
      page_size: 10,
      page_start: 0,
      page_end: 10,
      hide_next: false,
      hide_prev: true,
    };

    const vocabolario = this.vocabularyService.search(term, this.lang);
    console.log(vocabolario);
    this.results.vocabulary = this.vocabularyService
      .search(term, this.lang)
      .slice();
    return this.LodService.search(term, this.lang).then(
      (lodResults) => {
        this.results.lods = [];
        lodResults.search.forEach((l) => {
          const t = {
            group: "term",
            creator_type: "user",
            name: l.label,
            description: l.description,
            iri: l.concepturi,
            source: "lod",
          };

          vocabolario.push(t);
          this.results.lods.push(t);
        });

        this.results.vocabulary.sort(
          AppModalInsertTermtagComponent._sort_alpha
        );
        this.results.lods.sort(AppModalInsertTermtagComponent._sort_alpha);

        this.results.show = !this.results.vocabulary.length ? "l" : "v";

        if (!this.results.vocabulary.length) {
          this.results.vocabulary_nav.hide_next = true;
          this.results.vocabulary_nav.hide_prev = true;
        }

        if (!this.results.lods.length) {
          this.results.lods_nav.hide_next = true;
          this.results.lods_nav.hide_prev = true;
        }

        if (this.results.vocabulary.length || this.results.lods.length) {
          this.p.open();
        } else {
          this.p.close();
        }
        return vocabolario;
      },
      function () {
        console.log("An error occurred in LodService.search");
      }
    );
  }

  show_results(flag) {
    this.results.show = flag;
  }

  /**
   * typeahead result formatter
   * @param {{name: string}} result
   * @returns {string}
   */
  formatter = (result: { name: string }) => result.name;

  /**
   * Disable the button if there is a term equal to the search term among the tags found.
   */
  term_add_disable() {
    return (
      this.ricerca_key &&
      this.ricerca_key.name &&
      this.ricerca_risultati.filter(
        (r) => r.name.toLowerCase() === this.ricerca_key.name.toLowerCase()
      ).length
    );
  }

  /**
   * Adds the term to the list of terms to save
   * @param event
   */
  term_add(event) {
    let close_results = false;
    if (typeof event === "string") {
      event = { name: event };
      close_results = true;
    }
    if (event && event.name) {
      //  prevent duplication
      let existing = this.terms.some((t) => {
        return t.name.toLowerCase() === event.name.toLowerCase();
      });
      existing =
        existing ||
        this.terms_all.some((t) => {
          return t.name.toLowerCase() === event.name.toLowerCase();
        });
      if (existing) {
        this.add_tag.show("info", "This tag has already been added");
      } else {
        if (event.source === "vocabulary") {
          this.vocabularyService.toggle_term(event);
        }
        this.add_tag.hide();
        this.terms.push(this.vocabularyService.annotation_create(event));
        // reset input field
        this.ricerca_model = "";
      }
      if (close_results) {
        this.p.close();
      }
    }
  }

  /**
   * Removes a term from the term list.
   * @param term
   */
  term_remove(term) {
    this.terms = this.terms.filter((t) => t.name !== term.name);
    this.vocabularyService.deselect_term(term);
  }

  /**
   * Una voce di ricerca viene cliccata
   * @param term
   */
  term_selected(term) {
    this.term_add(term);
    this.p.close();
  }

  /**
   * esegue il salvataggio
   */
  salva() {
    this.AnnotationsService.create_tag(
      this.data.shots.map((s) => s.id),
      this.terms,
      this.media_type,
      (err, response) => {
        if (err) {
          return this.save_result.show("error");
        }
        response.some((r) => {
          if (!r.errors) {
            this.shots_update.emit(r.data);
            this.terms.forEach((t) => this.terms_all.push(t));
            this.terms = [];
            this.save_result.show("success", "Tag added successfully");
            return true;
          }
        });
      }
    );
  }

  hide_app_info() {
    this.save_result.visible = false;
  }

  nav_next(obj) {
    const results = this.results[obj];
    const nav = this.results[`${obj}_nav`];
    if (nav.page_end < results.length) {
      nav.page_start += nav.page_size;
      nav.page_end += nav.page_size;
    }
    AppModalInsertTermtagComponent.nav_show_buttons(results, nav);
  }

  nav_prev(obj) {
    const results = this.results[obj];
    const nav = this.results[`${obj}_nav`];
    if (nav.page_start >= nav.page_size) {
      nav.page_start -= nav.page_size;
      nav.page_end -= nav.page_size;
    }
    AppModalInsertTermtagComponent.nav_show_buttons(results, nav);
  }

  static nav_show_buttons(results, nav) {
    if (results.length) {
      nav.hide_prev = nav.page_start < nav.page_size;
      nav.hide_next =
        nav.page_start >= results.length - nav.page_size ||
        results.length < nav.page_size;
    } else {
      nav.hide_prev = true;
      nav.hide_next = true;
    }
  }

  ngOnInit() {
    this.subject.pipe(debounceTime(300)).subscribe((searchTextValue) => {
      this.search_vocabulary_and_lods(searchTextValue);
    });
  }

  ngOnChanges() {
    this.terms_all = this.AnnotationsService.merge(this.data.shots, "tags");

    /*this.vocabularyService.get((vocabolario) => {
      this.vocabolario = vocabolario;
    });*/
    this.ricerca_model = "";
    this.terms = [];
    this.ricerca_risultati = [];
    if (this.search_field) {
      this.search_field.nativeElement.value = "";
    }
  }

  ngAfterViewInit() {
    // this.vocabolario_visualizza = true;
    this.ref.detectChanges();
  }

  static _sort_alpha(a, b) {
    if (a.name.toLowerCase() < b.name.toLowerCase()) return -1;
    if (a.name.toLowerCase() > b.name.toLowerCase()) return 1;
    return 0;
  }
}
