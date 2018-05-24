import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
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

  constructor(private formBuilder: FormBuilder) {
    this.searchForm = this.formBuilder.group({
      searchTerm: [''],
      itemType: ['', Validators.required],
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
    console.log('apply filter');
  }

  resetFiltersToDefault() {
    console.log('reset filter to default');
  }

}