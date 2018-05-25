import { Component, OnInit, Output, EventEmitter} from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { SearchFilter } from '../../services/catalog.service'
import { IPRStatuses, Providers } from '../../services/data';
import { Observable } from 'rxjs/Observable';
import 'rxjs/add/observable/combineLatest';

@Component({
  selector: 'search-filter',
  templateUrl: './search-filter.component.html',
  styleUrls: ['./search-filter.component.css']
})
export class SearchFilterComponent implements OnInit {
  searchForm: FormGroup;
  iprstatuses = IPRStatuses;
  cities = []

  @Output() onFilterChange: EventEmitter<SearchFilter> = new EventEmitter<SearchFilter>();

  constructor(private formBuilder: FormBuilder) {
    this.searchForm = this.formBuilder.group({
      searchTerm: [''],
      itemType: ['video', Validators.required],
      terms: [''],
      city: [''],
      productionYear: [''],
      iprstatus: ['']
    });
    for (let i = 0; i < Providers.length; i++) this.cities.push(Providers[i].city.name);
  }

  ngOnInit() {
  }

  applyFilter() {
    let filter = this.searchForm.value;
    if (filter.iprstatus === '') { filter.iprstatus = null; }
    if (filter.city === '') { filter.city = null; }
    this.onFilterChange.emit(filter);
  }

  resetFiltersToDefault() {
    console.log('reset filter to default');
  }

}