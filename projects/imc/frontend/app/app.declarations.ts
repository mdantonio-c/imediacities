
import { CustomNavbarComponent } from './app.custom.navbar';
import { CustomBrandComponent } from './app.custom.navbar';
import { ArchiveComponent } from './imc.archive'
import { ArchivesListComponent } from './imc.archives.list'
import {AppVideoComponent} from "./components/app-video/app.video";
import {ProviderToCityPipe} from "./pipes/ProviderToCity";

export const declarations: any[] = [
	CustomNavbarComponent, CustomBrandComponent, ArchivesListComponent, ArchiveComponent, AppVideoComponent,
	ProviderToCityPipe
];