import { Component, Input, OnInit, Output, EventEmitter } from "@angular/core";
import { Vocabulary, Annotation } from "../../../types";
import { AppVocabularyService } from "../../../services/app-vocabulary";

@Component({
  selector: "app-tree-view",
  templateUrl: "app-tree-view.html",
})
export class AppTreeViewComponent implements OnInit {
  @Input() lang: string = "en";
  @Input() terms: Annotation[] = [];

  vocabulary: Vocabulary;
  @Output() updateTerms: EventEmitter<Annotation[]> = new EventEmitter<
    Annotation[]
  >();
  @Output() updateVocabulary: EventEmitter<Vocabulary> = new EventEmitter<
    Vocabulary
  >();

  constructor(private vocabularyService: AppVocabularyService) {}

  ngOnInit() {
    this.vocabularyService.get((data) => {
      this.vocabulary = data;
      this.updateVocabulary.emit(this.vocabulary);
    });
  }

  /**
   * Manage the visibility of the vocabulary category terms (elements WITH children) on click.
   * @param term
   * @param parent
   */
  toggleCategory(term, parent = null) {
    let visibility = !term.open;
    this.vocabulary.terms.forEach((t) => {
      t.open = false;
    });
    if (parent) {
      parent.open = true;
      if (parent.hasOwnProperty("children")) {
        parent.children.forEach((c) => {
          c.open = false;
        });
      }
    }
    term.open = visibility;
  }

  /**
   * Manage the click on the vocabulary terms (elements WITHOUT children).
   * @param term
   */
  toggleTerm(term) {
    term.selected = !term.selected;
    if (term.selected) {
      if (this.terms.filter((t) => t.iri === term.id).length === 0) {
        this.terms.push(this.vocabularyService.annotation_create(term));
      }
    } else {
      // remove from the terms list
      this.terms = this.terms.filter((t) => t.iri !== term.id);
    }
    this.updateTerms.emit(this.terms);
  }

  /**
   * Naive solution to check if a category has a sub-category.
   * As ONLY leaf terms have an id, check this on the first node of the list.
   * @param category
   */
  hasSubCategory(category): boolean {
    return category.children[0].hasOwnProperty("id") ? false : true;
  }
}
