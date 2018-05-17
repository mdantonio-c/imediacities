
import { Routes } from '@angular/router';

import { AuthGuard } from '/rapydo/src/app/app.auth.guard';

import { ArchivesListComponent } from './imc.archives.list'
import {AppMediaComponent} from "./components/app-media/app-media";


export const appRoutes: Routes = [

  {
    path: 'new/archives',
    component: ArchivesListComponent,
    canActivate: [AuthGuard],
    data: {role: 'admin_root'}
  },
    {
        path: 'new/video',
        component: AppMediaComponent
    }
    
];
