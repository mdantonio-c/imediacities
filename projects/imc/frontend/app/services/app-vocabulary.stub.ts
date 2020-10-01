import { Observable, of } from "rxjs";
import { Injectable } from "@angular/core";
import { HttpClient } from "@angular/common/http";
import { AppVocabularyService } from "./app-vocabulary";
import { AppLodService } from "./app-lod";

@Injectable()
export class AppVocabularyServiceStub extends AppVocabularyService {
  constructor() {
    super({} as HttpClient, {} as AppLodService);
  }
}
