import { Component, OnInit, ViewChild } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { NotificationService } from '/rapydo/src/app/services/notification';
import { Providers } from '../../catalog/services/data';
import { CatalogService, SearchFilter } from '../../catalog/services/catalog.service'
import { ListsService } from '../../services/lists.service';
import { NgbDropdown } from '@ng-bootstrap/ng-bootstrap';
import { MultiItemCarouselComponent } from './multi-item-carousel/multi-item-carousel.component';
import { ItemDetail } from './item-detail/item-detail.component';

@Component({
	selector: 'user-workspace',
	templateUrl: 'user-workspace.html',
	styleUrls: ['./user-workspace.css']
})
export class UserWorkspaceComponent implements OnInit {

	cities: string[] = [];
	selectedCity: string = "";
	cityFilter: SearchFilter = {};
	countCityResults: number = 0;
	countListResults: number = 0;
    countListItemsResults: number;
	listForm: FormGroup;
	private selectedList: ItemDetail;
	/**
     * Reference to NgbDropdown component for creating a new user list
     */
	@ViewChild('newListDrop') listDropdown: NgbDropdown;
	/**
     * Reference to my list
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
                this.countListItemsResults = undefined;
        		this.selectedList = list;
        	})
	}

	onCityChange(newValue) {
		this.selectedCity = newValue;
		this.cityFilter = (newValue !== '') ? { city: newValue } : {};
	}

	countChangedHandler(newCount) {
		this.countCityResults = newCount;
	}

	countListHandler(newCount) {
		this.countListResults = newCount;
	}

    countListItemsHandler(newCount) {
        this.countListItemsResults = newCount;
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

    closeItemList(listId: string) {
        if (this.selectedList && listId === this.selectedList.id) {
            console.log(`close item list for <${listId}>`);
            this.listItemsComp.close();
            this.selectedList = undefined;
        }
    }

    private refreshMyLists() {
    	this.myListsComp.load();
    }

    private resetForm() {
        this.listForm.reset({ 'name': '', 'description': '' });
    }
}