import { NguiMapModule} from '@ngui/map';
import { HolderJsModule } from 'angular2-holderjs/component';

export const imports: any[] = [
  NguiMapModule.forRoot({apiUrl: 'https://maps.google.com/maps/api/js?libraries=places&key=AIzaSyCkSQ5V_EWELQ6UCvVGBwr3LCriTAfXypI'}),
  HolderJsModule
];
