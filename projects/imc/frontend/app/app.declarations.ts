
import { CustomNavbarComponent } from './app.custom.navbar';
import { CustomBrandComponent } from './app.custom.navbar';
import { ArchiveComponent } from './imc.archive'
import { ArchivesListComponent } from './imc.archives.list'

import {ProviderToCityPipe} from "./pipes/ProviderToCity";

import {AppMediaComponent} from "./components/app-media/app-media";
import {AppMediaTopBarComponent} from "./components/app-media/app-media-top-bar/app-media-top-bar";

import {AppPictureComponent} from "./components/app-media/app-picture/app-picture";
import {AppVideoTagComponent} from "./components/app-media/app-video-tag/app-video-tag";
import {AppVideoShotComponent} from "./components/app-media/app-video-shot/app-video-shot";
import {AppMediaMapComponent} from "./components/app-media/app-media-map/app-media-map";
import {AppMediaInfoComponent} from "./components/app-media/app-media-info/app-media-info";
import {AppMediaTagsComponent} from "./components/app-media/app-media-tags/app-media-tags";

import {AppVideoPlayerComponent} from "./components/app-media/app-video-player/app-video-player";
import {AppVideoControlPlayComponent} from 		"./components/app-media/app-video-controls/app-video-control-play/app-video-control-play";
import {AppVideoControlGotoStartComponent} from "./components/app-media/app-video-controls/app-video-control-goto-start/app-video-control-goto-start";
import {AppVideoControlGotoEndComponent} from 	"./components/app-media/app-video-controls/app-video-control-goto-end/app-video-control-goto-end";
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
import {AppModaleComponent} from "./components/app-modale/app-modale";
import {AppMediaModal} from "./components/app-media/app-media-modals/app-media-modal";
import {NoCommaPipe} from "./pipes/NoComma";


export const declarations: any[] = [
	CustomNavbarComponent, CustomBrandComponent, ArchivesListComponent, ArchiveComponent,
	ProviderToCityPipe,
	NoCommaPipe,
	AppModaleComponent,
	AppMediaComponent,
    AppMediaTopBarComponent,
	AppPictureComponent,
	AppVideoTagComponent,
	AppVideoShotComponent,
    AppMediaModal,
	AppMediaAnnotationComponent,
	AppMediaMapComponent,
	AppModalAllAnnotationsComponent,
	AppModalInsertGeotagComponent,
	AppModalInsertLinkComponent,
	AppModalInsertNoteComponent,
	AppModalInsertReferenceComponent,
    AppModalInsertTermtagComponent,
	AppMediaInfoComponent,
	AppMediaTagsComponent,
    AppVideoPlayerComponent,
    AppVideoControlPlayComponent,
    AppVideoControlGotoEndComponent,
	AppVideoControlGotoStartComponent,
    AppVideoControlProgressBarComponent,
	AppVideoControlFforwardComponent,
	AppVideoControlFrewindComponent,
	AppVideoControlTimeMarkersComponent,
	AppVideoControlTimerangeComponent,
	AppVideoControlVolumeComponent,
	AppVideoControlFullscreenComponent
];