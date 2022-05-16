import { TestBed, inject } from "@angular/core/testing";

import { MediaUtilsService } from "./media-utils.service";

describe("MediaUtilsService", () => {
  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [MediaUtilsService],
    });
  });

  it("should be created", inject(
    [MediaUtilsService],
    (service: MediaUtilsService) => {
      expect(service).toBeTruthy();
    }
  ));
});
