import { Component, OnInit, ViewChild } from "@angular/core";
import { FormBuilder, FormGroup, Validators } from "@angular/forms";
import { AuthService } from "@rapydo/services/auth";
import { NotificationService } from "@rapydo/services/notification";
import { Providers } from "../../catalog/services/data";
import {
  CatalogService,
  SearchFilter,
} from "../../catalog/services/catalog.service";
import { ListsService } from "../../services/lists.service";
import { NgbDropdown } from "@ng-bootstrap/ng-bootstrap";
import { MultiItemCarouselComponent } from "./multi-item-carousel/multi-item-carousel.component";
import { ItemDetail } from "./item-detail/item-detail.component";
import { environment } from "@rapydo/../environments/environment";

@Component({
  selector: "user-workspace",
  templateUrl: "user-workspace.html",
  styleUrls: ["./user-workspace.css"],
})
export class UserWorkspaceComponent implements OnInit {
  cities: string[] = [];
  selectedCity: string = "";
  cityFilter: SearchFilter = {};
  taggedByMeFilter: SearchFilter = {
    annotated_by: { user: null, type: "TAG" },
  };
  notedByMeFilter: SearchFilter = {
    annotated_by: { user: null, type: "DSC" },
  };
  counters = {
    BY_CITIES: undefined,
    MY_LISTS: undefined,
    LIST_ITEMS: undefined,
    TAGGED_BY_ME: undefined,
    NOTED_BY_ME: undefined,
  };
  listForm: FormGroup;
  selectedList: ItemDetail;
  private user: any;
  readonly cityFilterDisabled = false;
  /**
   * Reference to NgbDropdown component for creating a new user list
   */
  @ViewChild("newListDrop", { static: false }) listDropdown: NgbDropdown;
  /**
   * Reference to my list
   */
  @ViewChild("mylists", { static: false })
  myListsComp: MultiItemCarouselComponent;
  /**
   * Reference to the list of items
   */
  @ViewChild("listItems", { static: false })
  listItemsComp: MultiItemCarouselComponent;

  constructor(
    private authService: AuthService,
    private catalogService: CatalogService,
    private listsService: ListsService,
    private formBuilder: FormBuilder,
    private notify: NotificationService
  ) {
    this.listForm = this.formBuilder.group({
      name: ["", Validators.required],
      description: ["", Validators.required],
    });
    listsService.listSelected$.subscribe((list) => {
      this.selectedList = list;
      this.counters.LIST_ITEMS = undefined;
    });
    if (environment.CUSTOM.FRONTEND_DISABLED_FILTERS) {
      const disabledFilters = environment.CUSTOM.FRONTEND_DISABLED_FILTERS.split(
        ","
      );
      this.cityFilterDisabled = disabledFilters.includes("city");
    }
  }

  onCityChange(newValue) {
    this.selectedCity = newValue;
    this.cityFilter = newValue !== "" ? { city: newValue } : {};
  }

  countChangedHandler(newCount, counter = "BY_CITIES") {
    this.counters[counter] = newCount;
    if (counter === "LIST_ITEMS") {
      // update nb_items for the current selected list
      this.selectedList.nb_items = newCount;
    }
  }

  ngOnInit() {
    this.user = this.authService.getUser();
    this.taggedByMeFilter.annotated_by.user = this.user.uuid;
    this.notedByMeFilter.annotated_by.user = this.user.uuid;
    for (let i = 0; i < Providers.length; i++)
      this.cities.push(Providers[i].city.name);
    this.cities = this.cities.sort();
  }

  createList() {
    console.log("create list", this.listForm.value);
    this.listsService.create(this.listForm.value).subscribe(
      (response) => {
        console.log("list created successfully", response);
        this.notify.showSuccess("List created successfully");
        this.listDropdown.close();
        this.refreshMyLists();
      },
      (error) => {
        console.error("There was an error creating list", error.errors);
        this.notify.showError(error);
      }
    );
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
    this.listForm.reset({ name: "", description: "" });
  }
}
