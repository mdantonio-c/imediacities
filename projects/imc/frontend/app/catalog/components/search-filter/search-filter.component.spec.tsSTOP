import { async, ComponentFixture, TestBed } from "@angular/core/testing";
import { ReactiveFormsModule, FormBuilder } from "@angular/forms";

import { SearchFilterComponent } from "./search-filter.component";
import { AppVocabularyService } from "../../../services/app-vocabulary";
import { AppVocabularyServiceStub } from "../../../services/app-vocabulary.stub";
import { CatalogService } from "../../services/catalog.service";
import { CatalogServiceStub } from "../../services/catalog.service.stub";

describe("SearchFilterComponent", () => {
  let component: SearchFilterComponent;
  let fixture: ComponentFixture<SearchFilterComponent>;
  // create new instance of FormBuilder
  const formBuilder: FormBuilder = new FormBuilder();

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [SearchFilterComponent],
      imports: [ReactiveFormsModule],
      providers: [
        { provide: CatalogService, useClass: CatalogServiceStub },
        { provide: AppVocabularyService, useClass: AppVocabularyServiceStub },
        { provide: FormBuilder, useValue: formBuilder },
      ],
    }).compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(SearchFilterComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });
});
