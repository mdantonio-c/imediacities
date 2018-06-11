
import {AppAnnotationsService} from "./services/app-annotations";
import {AppShotsService} from "./services/app-shots";
import {AppMediaService} from "./services/app-media";
import {AppVocabularyService} from "./services/app-vocabulary";
import {AppModaleService} from "./services/app-modale";
import {AppVideoControlsFastPlayService} from "./services/app-video-controls-fast-play";
import {ProviderToCityPipe} from "./pipes/ProviderToCity";
import {AppVideoService} from "./services/app-video";
import {AppLodService} from "./services/app-lod";

export const providers: any[] = [
    AppAnnotationsService,
    AppLodService,
    AppMediaService,
    AppModaleService,
    AppShotsService,
    AppVocabularyService,
    AppVideoService,
    AppVideoControlsFastPlayService,
    ProviderToCityPipe
];