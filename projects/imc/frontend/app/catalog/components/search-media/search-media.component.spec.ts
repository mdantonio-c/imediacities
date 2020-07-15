import { async, ComponentFixture, TestBed } from "@angular/core/testing";

import { SearchMediaComponent } from "./search-media.component";

describe("SearchMediaComponent", () => {
  let component: SearchMediaComponent;
  let fixture: ComponentFixture<SearchMediaComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [SearchMediaComponent],
    }).compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(SearchMediaComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });
});
