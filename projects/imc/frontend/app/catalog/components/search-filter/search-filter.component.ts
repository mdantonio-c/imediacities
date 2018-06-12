import { Component, OnInit, Output, EventEmitter } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { SearchFilter, CatalogService } from '../../services/catalog.service'
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
  minProductionYear: number = 1890;
  maxProductionYear: number = 1999;

  @Output() onFilterChange: EventEmitter<SearchFilter> = new EventEmitter<SearchFilter>();

  constructor(
    private formBuilder: FormBuilder,
    private vocabularyService: AppVocabularyService,
    private catalogService: CatalogService) {
    this.searchForm = this.formBuilder.group({
      searchTerm: [''],
      videoType: [true],
      imageType: [false],
      term: [''],
      city: [''],
      productionYearFrom: [1890],
      productionYearTo: [1999],
      iprstatus: [null]
    });
  }

  ngOnInit() {
    for (let i = 0; i < Providers.length; i++) this.cities.push(Providers[i].city.name);
    this.vocabularyService.get((vocabulary) => { 
      this.vocabulary = vocabulary;
      for (let t of this.terms) {
        this.vocabularyService.select_term(t);
      }
    });
    this.searchForm.setValue(this.toForm(this.catalogService.filter));
  }

  private toForm(filter: SearchFilter) {
    let res = {
      searchTerm: filter.searchTerm,
      videoType: (filter.itemType === 'all' || filter.itemType === 'video') ? true : false,
      imageType: (filter.itemType === 'all' || filter.itemType === 'image') ? true : false,
      term: '',
      city: this.providerToCity(filter.provider),
      productionYearFrom: filter.productionYearFrom,
      productionYearTo: filter.productionYearTo,
      iprstatus: filter.iprstatus
    }
    this.terms = [];
    for (let t of filter.terms) {
      let entry = (!t.iri) ? t.label : { iri: t.iri, name: t.label };
      this.addTerm(entry);
    }
    return res;
  }

  verifyItemType(type) {
    //console.log('verifyItemType: type=' + type);
    let form = this.searchForm.value;
    var newVideoType: boolean = form.videoType;
    var newImageType: boolean = form.imageType;

    if (type == 'image') {
      newImageType = !newImageType;
    }
    if (type == 'video') {
      newVideoType = !newVideoType;
    }
    //console.log('newVideoType=' + newVideoType);
    //console.log('newImageType=' + newImageType);
    if (!newVideoType && !newImageType) {
      return false;
    }
    return true;
  }

  applyFilter() {
    let form = this.searchForm.value;
    /*console.log('Form', form);*/
    let filter: SearchFilter = {
      searchTerm: null,
      itemType: null,
      terms: [],
      provider: null,
      country: null,
      productionYearFrom: form.productionYearFrom,
      productionYearTo: form.productionYearTo,
      iprstatus: null
    }
    if (form.searchTerm !== '') { filter.searchTerm = form.searchTerm; }
    // item type
    if (form.videoType && form.imageType) {
      filter.itemType = 'all';
    } else if (form.videoType) {
      filter.itemType = 'video';
    } else if (form.imageType) {
      filter.itemType = 'image';
    }
    for (let t of this.terms) {
      filter.terms.push({ iri: t.iri, label: t.name });
    }
    if (form.city !== '') { filter.provider = this.cityToProvider(form.city); }
    if (form.iprstatus !== '') { filter.iprstatus = form.iprstatus; }
    this.onFilterChange.emit(filter);
  }

  resetFiltersToDefault() {
    this.catalogService.reset();
    this.searchForm.setValue(this.toForm(this.catalogService.filter));
    this.vocabularyService.reset();
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

  private providerToCity(provider) {
    let c = null;
    if (provider === 'TTE') { c = 'Athens'; }
    else if (provider === 'CCB') { c = 'Bologna'; }
    else if (provider === 'CRB') { c = 'Brussels'; }
    else if (provider === 'DFI') { c = 'Copenhagen'; }
    else if (provider === 'DIF') { c = 'Frankfurt am Main'; }
    else if (provider === 'FDC') { c = 'Barcelona'; }
    else if (provider === 'MNC') { c = 'Turin'; }
    else if (provider === 'OFM') { c = 'Vienna'; }
    else if (provider === 'SFI') { c = 'Stockholm'; }
    return c;
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
   * @param $event
   */
  selectTerm($event) {
    $event.preventDefault();
    this.addTerm($event.item);
    this.vocabularyService.select_term($event.item);
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
  }

  removeTerm(term) {
    this.terms = this.terms.filter(t => t.name !== term.name);
    if (term.iri) {
      this.vocabularyService.deselect_term(term);
    }
  }

}