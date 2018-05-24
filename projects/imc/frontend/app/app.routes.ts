
import { Routes } from '@angular/router';

import { AuthGuard } from '/rapydo/src/app/app.auth.guard';

import { ArchivesListComponent } from './imc.archives.list';
import { CatalogComponent } from './catalog/catalog.component';
import { AppMediaComponent } from './components/app-media/app-media';

export const appRoutes: Routes = [
	{
		path: 'app/admin/archives',
		component: ArchivesListComponent,
		canActivate: [AuthGuard],
		data: { role: 'admin_root' }
	},
	{ path: 'app/catalog', component: CatalogComponent },
	{ path: 'app/catalog/:uuid', component: AppMediaComponent }

];
