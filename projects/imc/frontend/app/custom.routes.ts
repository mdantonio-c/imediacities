
import { Routes } from '@angular/router';

import { AuthGuard } from '/rapydo/src/app/app.auth.guard';

import { ArchivesListComponent } from './components/admin/archive/archives.list';
import { AdminGroupsComponent } from './components/admin/groups';
import { UploadComponent } from './components/upload/upload';

import { CatalogComponent } from './catalog/catalog.component';
import { AppMediaComponent } from './components/app-media/app-media';
import { UserWorkspaceComponent } from './components/user-workspace/user-workspace';

export const appRoutes: Routes = [
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
