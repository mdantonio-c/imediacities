
import { Routes } from '@angular/router';

import { AuthGuard } from '/rapydo/src/app/app.auth.guard';

import { ArchivesListComponent } from './imc.archives.list'
import {AppMediaComponent} from "./components/app-media/app-media";


export const appRoutes: Routes = [

  {
        path: 'app/admin/archives',
        component: ArchivesListComponent,
        canActivate: [AuthGuard],
        data: {role: 'admin_root'}
  },
    {
        path: 'app/catalog/videos/:uuid',
        canActivate: [AuthGuard],
        component: AppMediaComponent
    },
    {
        path: 'app/catalog/images/:uuid',
        canActivate: [AuthGuard],
        component: AppMediaComponent
    }
    
];
