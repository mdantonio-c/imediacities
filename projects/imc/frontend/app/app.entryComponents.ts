import { CatalogComponent } from './catalog/catalog.component';
import { SearchFilterComponent } from './catalog/components/search-filter/search-filter.component';
import { SliderRangeComponent } from './catalog/components/search-filter/slider-range/slider-range.component';
import { SearchNavbarComponent } from './catalog/components/search-navbar/search-navbar.component';
import { SearchThumbnailComponent } from './catalog/components/search-thumbnail/search-thumbnail.component';
import { SearchMediaComponent } from './catalog/components/search-media/search-media.component';
import { SearchMapComponent } from './catalog/components/search-map/search-map.component';
import { SearchTimelineComponent } from './catalog/components/search-timeline/search-timeline.component';
import {AppModalInsertTermtagComponent} from "./components/app-media/app-media-modals/app-modal-insert-termtag/app-modal-insert-termtag";
import {AppModalInsertGeotagComponent} from "./components/app-media/app-media-modals/app-modal-insert-geotag/app-modal-insert-geotag";
import {AppModalInsertNoteComponent} from "./components/app-media/app-media-modals/app-modal-insert-note/app-modal-insert-note";
import {AppModalInsertLinkComponent} from "./components/app-media/app-media-modals/app-modal-insert-link/app-modal-insert-link";
import {AppModalInsertReferenceComponent} from "./components/app-media/app-media-modals/app-modal-insert-reference/app-modal-insert-reference";

export const entryComponents: any[] = [
	CatalogComponent,
    SearchFilterComponent,
    SliderRangeComponent,
    SearchNavbarComponent,
    SearchThumbnailComponent,
    SearchMediaComponent,
    SearchMapComponent,
    SearchTimelineComponent,
    AppModalInsertTermtagComponent,
    AppModalInsertGeotagComponent,
    AppModalInsertNoteComponent,
    AppModalInsertLinkComponent,
    AppModalInsertReferenceComponent,
];
