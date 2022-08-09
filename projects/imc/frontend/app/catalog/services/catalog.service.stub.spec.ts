import { TestBed, inject } from "@angular/core/testing";

import { CatalogServiceStub } from "./catalog.service.stub";

describe("CatalogStubService", () => {
  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [CatalogServiceStub],
    });
  });

  it("should be created", inject(
    [CatalogServiceStub],
    (service: CatalogServiceStub) => {
      expect(service).toBeTruthy();
    }
  ));
});
