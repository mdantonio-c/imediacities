
import { Routes } from '@angular/router';

import { AuthGuard } from '/rapydo/src/app/app.auth.guard';

import { ArchivesListComponent } from './components/admin/archive/archives.list';
import { AdminGroupsComponent } from './components/admin/groups';

import { CatalogComponent } from './catalog/catalog.component';
import { AppMediaComponent } from './components/app-media/app-media';

export const appRoutes: Routes = [
	{
		path: 'app/admin/archives',
		component: ArchivesListComponent,
		canActivate: [AuthGuard],
		data: { role: 'admin_root' }
	},
	{
		path: 'app/admin/groups',
		component: AdminGroupsComponent,
		canActivate: [AuthGuard],
		data: { role: 'admin_root' }
	},
	{ path: 'app/catalog', component: CatalogComponent },
	{ path: 'app/catalog/images/:uuid', component: AppMediaComponent },
	{ path: 'app/catalog/videos/:uuid', component: AppMediaComponent },
	{ path: 'app', redirectTo: '/app/catalog', pathMatch: 'full' },
	{ path: '', redirectTo: '/app/catalog', pathMatch: 'full' }

];
