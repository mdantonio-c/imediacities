import { async, ComponentFixture, TestBed } from "@angular/core/testing";

import { MapInfowindowComponent } from "./map-infowindow.component";

describe("MapInfowindowComponent", () => {
  let component: MapInfowindowComponent;
  let fixture: ComponentFixture<MapInfowindowComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [MapInfowindowComponent],
    }).compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(MapInfowindowComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });
});
