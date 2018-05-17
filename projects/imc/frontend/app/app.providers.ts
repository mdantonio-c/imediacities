
import {AppShotsService} from "./services/app-shots";
import {AppVideoService} from "./services/app-video";
import {AppVocabularyService} from "./services/app-vocabulary";
import {AppVideoRangePlayer} from "./services/app-video-range-player";
import {AppModaleService} from "./services/app-modale";
import {AppAnnotationsService} from "./services/app-annotations";

export const providers: any[] = [
    AppAnnotationsService,
    AppShotsService,
    AppVideoService,
    AppVocabularyService,
    AppVideoRangePlayer,
    AppModaleService
];
