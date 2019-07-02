import { NgModule, ModuleWithProviders } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { RapydoModule } from '/rapydo/src/app/rapydo.module';
import { AuthGuard } from '/rapydo/src/app/app.auth.guard';

import { HttpClientJsonpModule } from '@angular/common/http';
import { NguiMapModule} from '@ngui/map';
import { HolderJsModule } from 'angular2-holderjs/component';
import { IonRangeSliderModule } from "ng2-ion-range-slider";
import { FileSelectDirective, FileDropDirective } from 'ng2-file-upload';
import { SlickCarouselModule } from 'ngx-slick-carousel';

import { ArchiveComponent } from './components/admin/archive/archive'
import { ArchivesListComponent } from './components/admin/archive/archives.list'
import { AdminGroupsComponent } from './components/admin/groups';
import { UploadComponent } from './components/upload/upload';
import { UserWorkspaceComponent } from './components/user-workspace/user-workspace';
import { MultiItemCarouselComponent } from './components/user-workspace/multi-item-carousel/multi-item-carousel.component';
import { ItemDetailComponent } from './components/user-workspace/item-detail/item-detail.component';

import { CatalogComponent } from './catalog/catalog.component';
import { SearchFilterComponent } from './catalog/components/search-filter/search-filter.component';
import { SearchNavbarComponent } from './catalog/components/search-navbar/search-navbar.component';
import { SearchThumbnailComponent } from './catalog/components/search-thumbnail/search-thumbnail.component';
import { SearchMediaComponent } from './catalog/components/search-media/search-media.component';
import { SearchMapComponent } from './catalog/components/search-map/search-map.component';
import { SearchTimelineComponent } from './catalog/components/search-timeline/search-timeline.component';
import { SearchMediaTagComponent } from './catalog/components/search-media-tag/search-media-tag.component';
import { SliderRangeComponent } from './catalog/components/search-filter/slider-range/slider-range.component';

import {ProviderToCityPipe} from "./pipes/ProviderToCity";
import {DurationPipe} from "./pipes/duration.pipe";
import {SecondsToTimePipe} from "./pipes/secondsToTime.pipe";

import {AppMediaComponent} from "./components/app-media/app-media";
import {AppMediaTopBarComponent} from "./components/app-media/app-media-top-bar/app-media-top-bar";
import {AppAddToListComponent} from "./components/app-add-to-list/app-add-to-list";

import {AppPictureComponent} from "./components/app-media/app-picture/app-picture";
import {AppVideoTagComponent} from "./components/app-media/app-video-tag/app-video-tag";
import {AppVideoShotComponent} from "./components/app-media/app-video-shot/app-video-shot";
import {AppMediaMapComponent} from "./components/app-media/app-media-map/app-media-map";
import {AppMediaInfoComponent} from "./components/app-media/app-media-info/app-media-info";
import {AppMediaTagsComponent} from "./components/app-media/app-media-tags/app-media-tags";

import {AppVideoPlayerComponent} from "./components/app-media/app-video-player/app-video-player";
import {AppVideoControlPlayComponent} from     "./components/app-media/app-video-controls/app-video-control-play/app-video-control-play";
import {AppVideoControlGotoStartComponent} from "./components/app-media/app-video-controls/app-video-control-goto-start/app-video-control-goto-start";
import {AppVideoControlGotoEndComponent} from   "./components/app-media/app-video-controls/app-video-control-goto-end/app-video-control-goto-end";
import {AppVideoControlProgressBarComponent} from "./components/app-media/app-video-controls/app-video-control-progress-bar/app-video-control-progress-bar";
import {AppVideoControlFforwardComponent} from "./components/app-media/app-video-controls/app-video-control-fforward/app-video-control-fforward";
import {AppVideoControlFrewindComponent} from "./components/app-media/app-video-controls/app-video-control-frewind/app-video-control-frewind";
import {AppVideoControlTimeMarkersComponent} from "./components/app-media/app-video-controls/app-video-control-time-markers/app-video-control-time-markers";
import {AppVideoControlTimerangeComponent} from "./components/app-media/app-video-controls/app-video-control-timerange/app-video-control-timerange";
import {AppVideoControlVolumeComponent} from "./components/app-media/app-video-controls/app-video-control-volume/app-video-control-volume";
import {AppMediaAnnotationComponent} from "./components/app-media/app-media-annotation/app-media-annotation";
import {AppVideoControlFullscreenComponent} from "./components/app-media/app-video-controls/app-video-control-fullscreen/app-video-control-fullscreen";
import {AppModalInsertGeotagComponent} from "./components/app-media/app-media-modals/app-modal-insert-geotag/app-modal-insert-geotag";
import {AppModalInsertTermtagComponent} from "./components/app-media/app-media-modals/app-modal-insert-termtag/app-modal-insert-termtag";
import {AppModalInsertNoteComponent} from "./components/app-media/app-media-modals/app-modal-insert-note/app-modal-insert-note";
import {AppModalAllAnnotationsComponent} from "./components/app-media/app-media-modals/app-modal-all-annotations/app-modal-all-annotations";
import {AppModalInsertLinkComponent} from "./components/app-media/app-media-modals/app-modal-insert-link/app-modal-insert-link";
import {AppModalInsertReferenceComponent} from "./components/app-media/app-media-modals/app-modal-insert-reference/app-modal-insert-reference";
import {AppModalMoveCutComponent} from "./components/app-media/app-media-modals/app-modal-move-cut/app-modal-move-cut";
import {AppModaleComponent} from "./components/app-modale/app-modale";
import {AppMediaModal} from "./components/app-media/app-media-modals/app-media-modal";
import {NoCommaPipe} from "./pipes/NoComma";
import {AppModalListaShotsComponent} from "./components/app-media/app-media-modals/app-modal-lista-shots/app-modal-lista-shots";
// import {DropdownPositionDirective} from "./directives/dropdow-reposition";
import {AppVideoControlFpsComponent} from "./components/app-media/app-video-controls/app-video-control-fps/app-video-control-fps";
import {AppVideoControlSwitchComponent} from "./components/app-media/app-video-controls/app-video-control-switch/app-video-control-switch";
import {appVideoControlsDeclarations as VideoControlsDeclarations} from "./components/app-media/app-video-controls/app-video-controls-declarations";
import {InputNumericDirective} from "./directives/input-numeric";
import {AppModalTagCloudComponent} from "./components/app-media/app-media-modals/app-modal-tag-cloud/app-modal-tag-cloud";
import {InputSelectDirective} from "./directives/input-select";
import {AppMediaCommentiComponent} from "./components/app-media/app-media-commenti/app-media-commenti";
import {AppMediaRelatedItemsComponent} from "./components/app-media/app-media-related-items/app-media-related-items";
import {AppShotReferenceComponent} from "./components/app-media/app-shot-reference/app-shot-reference";
import {AppMediaMapWrapperComponent} from "./components/app-media/app-media-map-wrapper/app-media-map-wrapper";
import {AppExpansionPanelComponent} from "./components/app-expansion-panel/app-expansion-panel";
import {AppInfoComponent} from "./components/app-info/app-info";
import {AppNoteComponent} from "./components/app-note/app-note";
import {AppReferenceComponent} from "./components/app-reference/app-reference";
import {AppLinkComponent} from "./components/app-link/app-link";
import {AutoFocusDirective} from "./directives/auto-focus"

import {CatalogService} from './catalog/services/catalog.service';
import {MediaUtilsService} from './catalog/services/media-utils.service';
import {LocalStorageService} from './catalog/services/local-storage.service';
import {AppAnnotationsService} from "./services/app-annotations";
import {AppShotsService} from "./services/app-shots";
import {AppMediaService} from "./services/app-media";
import {AppVocabularyService} from "./services/app-vocabulary";
import {AppModaleService} from "./services/app-modale";
import {AppVideoControlsFastPlayService} from "./services/app-video-controls-fast-play";
import {AppVideoService} from "./services/app-video";
import {AppLodService} from "./services/app-lod";
import {ShotRevisionService} from "./services/shot-revision.service";
import {ListsService} from "./services/lists.service";


const routes: Routes = [
  {
    path: 'app/admin/archives',
    component: ArchivesListComponent,
    canActivate: [AuthGuard],
    runGuardsAndResolvers: 'always',
    data: { roles: ['admin_root'] }
  },
  {
    path: 'app/admin/groups',
    component: AdminGroupsComponent,
    canActivate: [AuthGuard],
    runGuardsAndResolvers: 'always',
    data: { roles: ['admin_root'] }
  },
  {
    path: 'app/upload',
    component: UploadComponent,
    canActivate: [AuthGuard],
    runGuardsAndResolvers: 'always',
    data: { roles: ['Archive'] }
  },
  {
    path: 'app/myWorkspace',
    component: UserWorkspaceComponent,
    canActivate: [AuthGuard],
    runGuardsAndResolvers: 'always',
    data: { roles: ['Researcher'] }
  },
  // { path: 'app/catalog', component: CatalogComponent, canActivate: [AuthGuard], runGuardsAndResolvers: 'always' },
  { path: 'app/catalog', component: CatalogComponent },

  // { path: 'app/catalog/images/:uuid', component: AppMediaComponent, canActivate: [AuthGuard], runGuardsAndResolvers: 'always' },
  { path: 'app/catalog/images/:uuid', component: AppMediaComponent },

  // { path: 'app/catalog/videos/:uuid', component: AppMediaComponent, canActivate: [AuthGuard], runGuardsAndResolvers: 'always' },
  { path: 'app/catalog/videos/:uuid', component: AppMediaComponent },

  { path: 'app', redirectTo: '/app/catalog', pathMatch: 'full' },
  { path: '', redirectTo: '/app/catalog', pathMatch: 'full' }

];

@NgModule({
  imports: [
    RapydoModule,
    RouterModule.forChild(routes),
    HttpClientJsonpModule,
    NguiMapModule.forRoot({apiUrl: 'https://maps.google.com/maps/api/js?libraries=places&key='+process.env.GMAP_KEY}),
    HolderJsModule,
    IonRangeSliderModule,
    SlickCarouselModule
  ],
  declarations: [
    ArchivesListComponent, ArchiveComponent,
    AdminGroupsComponent,
    UploadComponent,
    UserWorkspaceComponent,
    MultiItemCarouselComponent,
    ItemDetailComponent,
    CatalogComponent,
    SearchFilterComponent,
    SliderRangeComponent,
    SearchNavbarComponent,
    SearchThumbnailComponent,
    SearchMediaComponent,
    SearchMapComponent,
    SearchTimelineComponent,
    SearchMediaTagComponent,
    ProviderToCityPipe,
    NoCommaPipe,
    DurationPipe,
    SecondsToTimePipe,
    AppExpansionPanelComponent,
    AppInfoComponent,
    AppModaleComponent,
    AppMediaComponent,
    AppMediaTopBarComponent,
    AppAddToListComponent,
    AppPictureComponent,
    AppShotReferenceComponent,
    AppVideoTagComponent,
    AppVideoShotComponent,
    AppMediaModal,
    AppMediaAnnotationComponent,
    AppMediaCommentiComponent,
    AppMediaMapComponent,
    AppMediaMapWrapperComponent,
    AppMediaRelatedItemsComponent,
    AppModalAllAnnotationsComponent,
    AppModalInsertGeotagComponent,
    AppModalInsertLinkComponent,
    AppModalInsertNoteComponent,
    AppModalInsertReferenceComponent,
    AppModalMoveCutComponent,
    AppModalInsertTermtagComponent,
    AppModalListaShotsComponent,
    AppMediaInfoComponent,
    AppMediaTagsComponent,
    AppNoteComponent,
    AppReferenceComponent,
    AppLinkComponent,
    AppVideoPlayerComponent,
    AppModalTagCloudComponent,
    VideoControlsDeclarations,
//    DropdownPositionDirective,
    InputNumericDirective,
    InputSelectDirective,
    AutoFocusDirective,

    FileSelectDirective, FileDropDirective
  ],

  providers: [
    CatalogService,
    MediaUtilsService,
    LocalStorageService,
    AppAnnotationsService,
    AppLodService,
    ShotRevisionService,
    ListsService,
    AppMediaService,
    AppModaleService,
    AppShotsService,
    AppVocabularyService,
    AppVideoService,
    AppVideoControlsFastPlayService,
    ProviderToCityPipe
  ],

  entryComponents: [
    CatalogComponent,
    SearchFilterComponent,
    SearchNavbarComponent,
    SearchThumbnailComponent,
    SearchMediaComponent,
    SearchMapComponent,
    SearchTimelineComponent,
    SearchMediaTagComponent,
    AppModalInsertTermtagComponent,
    AppModalInsertGeotagComponent,
    AppModalInsertNoteComponent,
    AppModalInsertLinkComponent,
    AppModalInsertReferenceComponent,
    AppModalMoveCutComponent,
  ],
  exports: [
    RouterModule
  ]

})
export class CustomModule {
  static forRoot(): ModuleWithProviders {
    return {
      ngModule: CustomModule,
      providers: [
        CatalogService,
        MediaUtilsService,
        LocalStorageService,
        AppAnnotationsService,
        AppLodService,
        ShotRevisionService,
        ListsService,
        AppMediaService,
        AppModaleService,
        AppShotsService,
        AppVocabularyService,
        AppVideoService,
        AppVideoControlsFastPlayService,
        ProviderToCityPipe
      ],
    };
  }
} 
