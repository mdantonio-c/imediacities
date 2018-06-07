import { Component, OnInit, Output, EventEmitter } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { SearchFilter } from '../../services/catalog.service'
import { IPRStatuses, Providers } from '../../services/data';
import { SliderRangeComponent } from './slider-range/slider-range.component';
import { Observable } from 'rxjs/Observable';
import 'rxjs/add/observable/combineLatest';

@Component({
  selector: 'search-filter',
  templateUrl: './search-filter.component.html',
  styleUrls: ['./search-filter.component.css']
})
export class SearchFilterComponent implements OnInit {
  searchForm: FormGroup;
  iprstatuses: any[] = IPRStatuses;
  cities: string[] = [];
  minProductionYear: number = 1890;
  maxProductionYear: number = 1999;

  @Output() onFilterChange: EventEmitter<SearchFilter> = new EventEmitter<SearchFilter>();

  constructor(private formBuilder: FormBuilder) {}

  ngOnInit() {
    this.searchForm = this.formBuilder.group({
      searchTerm: [''],
      //itemTypes: [{video: true, image: false}],
      videoType: [true],
      imageType: [false],
      terms: [[]],
      city: [''],
      productionYearFrom: [1890],
      productionYearTo: [1999],
      iprstatus: [null]
    });
    for (let i = 0; i < Providers.length; i++) this.cities.push(Providers[i].city.name);
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
    let filter: SearchFilter = {
      searchTerm: null,
      itemType: null,
      terms: [],
      provider: null,
      country: null,
      productionYearFrom: form.productionYearFrom,
      productionYearTo: form.productionYearTo,
      iprstatus: form.iprstatus
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
    // TODO terms
    if (form.city !== '') { filter.provider = this.cityToProvider(form.city); }
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
    this.searchForm.get('productionYearTo').setValue(newVal, {emitEvent: false})
  }

  changeYearFrom(newVal) {
    this.searchForm.get('productionYearFrom').setValue(newVal, {emitEvent: false})
  }

}