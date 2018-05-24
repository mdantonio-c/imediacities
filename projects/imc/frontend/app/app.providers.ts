
import { CatalogService } from './catalog/services/catalog.service';
import {AppAnnotationsService} from "./services/app-annotations";
import {AppShotsService} from "./services/app-shots";
import {AppVideoService} from "./services/app-video";
import {AppVocabularyService} from "./services/app-vocabulary";
import {AppModaleService} from "./services/app-modale";
import {AppVideoControlsFastPlayService} from "./services/app-video-controls-fast-play";

export const providers: any[] = [
    CatalogService,
    AppAnnotationsService,
    AppShotsService,
    AppVideoService,
    AppVocabularyService,
    AppModaleService,
    AppVideoControlsFastPlayService
];
