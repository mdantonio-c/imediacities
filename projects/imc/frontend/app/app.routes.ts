
import { Routes } from '@angular/router';

import { AuthGuard } from '/rapydo/src/app/app.auth.guard';

import { ArchivesListComponent } from './imc.archives.list'

export const appRoutes: Routes = [

  {
    path: 'app/admin/archives',
    component: ArchivesListComponent,
    canActivate: [AuthGuard],
    data: {role: 'admin_root'}
  },

];
