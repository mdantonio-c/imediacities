import { async, ComponentFixture, TestBed } from "@angular/core/testing";
import { RouterTestingModule } from "@angular/router/testing";
import { Router } from "@angular/router";

import { CatalogComponent } from "./catalog.component";
import { CatalogService } from "./services/catalog.service";
import { CatalogServiceStub } from "./services/catalog.service.stub";
import { NotificationService } from "@rapydo/services/notification";
import { SSRService } from "@rapydo/services/ssr";

class NotificationServiceStub {}
class SSRServiceStub {}

describe("CatalogComponent", () => {
  let component: CatalogComponent;
  let fixture: ComponentFixture<CatalogComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [CatalogComponent],
      imports: [RouterTestingModule.withRoutes([])],
      providers: [
        { provide: CatalogService, useClass: CatalogServiceStub },
        { provide: NotificationService, useClass: NotificationServiceStub },
        { provide: SSRService, useClass: SSRServiceStub },
      ],
    }).compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(CatalogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });
});
