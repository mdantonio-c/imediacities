import { Component, OnInit, Output, EventEmitter, ElementRef } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { SearchFilter } from '../../services/catalog.service'
import { IPRStatuses, Providers } from '../../services/data';
import { SliderRangeComponent } from './slider-range/slider-range.component';
import { AppVocabularyService } from "../../../services/app-vocabulary";
import { Observable } from 'rxjs/Observable';
import { debounceTime, distinctUntilChanged, map } from 'rxjs/operators';

@Component({
  selector: 'search-filter',
  templateUrl: './search-filter.component.html',
  styleUrls: ['./search-filter.component.css']
})
export class SearchFilterComponent implements OnInit {
  searchForm: FormGroup;
  vocabulary;
  terms = [];
  iprstatuses: any[] = IPRStatuses;
  cities: string[] = [];
  itemTypes: string[] = ['video', 'image'];
  minProductionYear: number = 1890;
  maxProductionYear: number = 1999;

  @Output() onFilterChange: EventEmitter<SearchFilter> = new EventEmitter<SearchFilter>();

  constructor(
    private formBuilder: FormBuilder,
    private vocabularyService: AppVocabularyService,
    private el: ElementRef) {
    this.searchForm = this.formBuilder.group({
      searchTerm: [''],
      itemTypes: [['video'], Validators.required],
      term: [''],
      city: [''],
      productionYearFrom: [1890],
      productionYearTo: [1999],
      iprstatus: [null]
    });
    for (let i = 0; i < Providers.length; i++) this.cities.push(Providers[i].city.name);
  }

  ngOnInit() {
    this.vocabularyService.get((vocabulary) => { this.vocabulary = vocabulary });
  }

  applyFilter() {
    let form = this.searchForm.value;
    /*console.log('Form', form);*/
    let filter: SearchFilter = {
      searchTerm: null,
      itemType: 'video',
      terms: [],
      provider: null,
      country: null,
      productionYearFrom: form.productionYearFrom,
      productionYearTo: form.productionYearTo,
      iprstatus: null
    }
    if (form.searchTerm !== '') { filter.searchTerm = form.searchTerm; }
    if (form.itemTypes.length === 2) { filter.itemType = 'all'; }
    else { filter.itemType = form.itemTypes[0]; }
    for (let t of this.terms) {
      filter.terms.push({iri: t.iri, label: t.name});
    }
    if (form.city !== '') { filter.provider = this.cityToProvider(form.city); }
    if (form.iprstatus !== '') { filter.iprstatus = form.iprstatus; }
    this.onFilterChange.emit(filter);
  }

  resetFiltersToDefault() {
    console.log('reset filter to default');
  }

  private cityToProvider(city) {
    let p = null;
    if (city === 'Athens') { p = 'TTE'; }
    else if (city === 'Bologna') { p = 'CCB'; }
    else if (city === 'Brussels') { p = 'CRB'; }
    else if (city === 'Copenhagen') { p = 'DFI'; }
    else if (city === 'Frankfurt am Main') { p = 'DIF'; }
    else if (city === 'Barcelona') { p = 'FDC'; }
    else if (city === 'Turin') { p = 'MNC'; }
    else if (city === 'Vienna') { p = 'OFM'; }
    else if (city === 'Stockholm') { p = 'SFI'; }
    return p;
  }

  changeYearTo(newVal) {
    this.searchForm.get('productionYearTo').setValue(newVal, { emitEvent: false })
  }

  changeYearFrom(newVal) {
    this.searchForm.get('productionYearFrom').setValue(newVal, { emitEvent: false })
  }

  expandTerm(term, parent = null) {
    let val = !term.open;
    this.vocabulary.terms.forEach(t => { t.open = false; });
    if (parent) {
      parent.open = true;
      if (parent.hasOwnProperty('children')) {
        parent.children.forEach(c => { c.open = false })
      }
    }
    term.open = val;
  }

  vocabularyLeaf(term) {
    term.selected = !term.selected;

    if (term.selected) {
      this.terms.push(this.vocabularyService.annotation_create(term));
    } else {
      //  remove the term from the list
      this.terms = this.terms.filter(t => t.name !== term.label);
    }
  }

  /**
   * Search terms from the vocabulary.
   * @param {<string>} text$
   * @returns {any}
   */
  searchByTerm = (text$: Observable<string>) =>
    text$.pipe(
      debounceTime(300),
      distinctUntilChanged(),
      map(term => term === '' ? [] : this.vocabularyService.search(term))
    );

  /**
   * Format the search results.
   * @param {{name: string}} result
   * @returns {string}
   */
  formatter = (result: { name: string }) => result.name;

  /**
   * A search entry is clicked
   * @param term
   */
  selectTerm(term) {
    this.addTerm(term.item);
    this.vocabularyService.toggle_term(term.item);
  }

  addTerm(event) {
    if (typeof event === 'string') {
      event = { name: event }
    }
    if (event && event.name) {
      //  prevent duplication
      if (this.terms.filter(t => t.name.toLowerCase() === event.name.toLowerCase()).length === 0) {
        this.terms.push(
          this.vocabularyService.annotation_create(event)
        );
      }

    }
    // clear the input field
    this.searchForm.get('term').setValue('', { emitEvent: false });
    const input = this.el.nativeElement.querySelector('#tag-term');
    if (input) { input.value = ''; }
  }

  removeTerm(term) {
    this.terms = this.terms.filter(t => t.name !== term.name);
    if (term.iri) {
      this.vocabularyService.toggle_term(term);
    }
  }

}