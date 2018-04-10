
import { Routes } from '@angular/router';

import { AuthGuard } from '/rapydo/src/app/app.auth.guard';

import { ArchivesListComponent } from './imc.archives.list'
import {AppVideoComponent} from "./components/app-video/app.video";

export const appRoutes: Routes = [

  {
    path: 'new/archives',
    component: ArchivesListComponent,
    canActivate: [AuthGuard],
    data: {role: 'admin_root'}
  }, {
        path: 'new/video',
        component: AppVideoComponent
    }
    
];
