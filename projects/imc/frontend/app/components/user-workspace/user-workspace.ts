import { Component, OnInit, ViewChild } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { NotificationService } from '/rapydo/src/app/services/notification';
import { Providers } from '../../catalog/services/data';
import { CatalogService, SearchFilter } from '../../catalog/services/catalog.service'
import { ListsService } from '../../services/lists.service';
import { NgbDropdown } from '@ng-bootstrap/ng-bootstrap';
import { MultiItemCarouselComponent } from './multi-item-carousel/multi-item-carousel.component';

@Component({
	selector: 'user-workspace',
	templateUrl: 'user-workspace.html',
	styleUrls: ['./user-workspace.css']
})
export class UserWorkspaceComponent implements OnInit {

	cities: string[] = [];
	selectedCity: string = "Bologna";
	cityFilter: SearchFilter = { city: this.selectedCity };
	countCityResults: number = 0;
	countListResults: number = 0;
	listForm: FormGroup;
	selectedList;
	/**
     * Reference to NgbDropdown component
     */
	@ViewChild('newListDrop') listDropdown: NgbDropdown;
	/**
     * Reference to MyLists component
     */
	@ViewChild('mylists') myListsComp: MultiItemCarouselComponent;
    /**
     * Reference to the list of items
     */
    @ViewChild('listItems') listItemsComp: MultiItemCarouselComponent;

	constructor(
		private catalogService: CatalogService,
		private listsService: ListsService,
		private formBuilder: FormBuilder,
		private notify: NotificationService) {
		this.listForm = this.formBuilder.group({
            name: ['', Validators.required],
            description: ['', Validators.required]
        });
        listsService.listSelected$.subscribe(
        	list => {
        		console.log('Selected list', list);
        		this.selectedList = list;
                if (list === null) {
                    this.listItemsComp.slickModal.unslick();
                }
        	})
       	listsService.listDeleted$.subscribe(
        	listId => {
        		console.log('Deleted list', listId);
        	})
	}

	onCityChange(newValue) {
		this.selectedCity = newValue;
		this.cityFilter = { city: newValue };
	}

	countChangedHandler(newCount) {
		this.countCityResults = newCount;
	}

	countListHandler(newCount) {
		this.countListResults = newCount;
	}

	ngOnInit() {
		for (let i = 0; i < Providers.length; i++) this.cities.push(Providers[i].city.name);
    	this.cities = this.cities.sort();
	}

	createList() {
        console.log('create list', this.listForm.value);
        this.listsService.create(this.listForm.value).subscribe(response => {
            console.log('list created successfully', response);
            this.notify.showSuccess("List created successfully");
            this.listDropdown.close();
            this.refreshMyLists();
        }, error => {
            console.error('There was an error creating list', error.errors);
            this.notify.extractErrors(error, this.notify.ERROR);
        });
    }

    openListCreation() {
    	this.resetForm();
    }

    private refreshMyLists() {
    	this.myListsComp.load();
    }

    private resetForm() {
        this.listForm.reset({ 'name': '', 'description': '' });
    }
}