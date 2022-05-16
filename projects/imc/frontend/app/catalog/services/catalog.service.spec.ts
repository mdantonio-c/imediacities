import { TestBed, inject } from "@angular/core/testing";

import { CatalogService } from "./catalog.service";
import { ApiService } from "@rapydo/services/api";
import { LocalStorageService } from "./local-storage.service";

class ApiServiceStub {}
class LocalStorageServiceStub {}

describe("CatalogService", () => {
  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        CatalogService,
        { provide: ApiService, useClass: ApiServiceStub },
        { provide: LocalStorageService, useClass: LocalStorageServiceStub },
      ],
    });
  });

  it("should be created", inject(
    [CatalogService],
    (service: CatalogService) => {
      expect(service).toBeTruthy();
    }
  ));
});
