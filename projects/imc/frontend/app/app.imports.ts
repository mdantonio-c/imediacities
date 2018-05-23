import { NguiMapModule} from '@ngui/map';

export const imports: any[] = [
  NguiMapModule.forRoot({apiUrl: 'https://maps.google.com/maps/api/js?libraries=places&key=AIzaSyCkSQ5V_EWELQ6UCvVGBwr3LCriTAfXypI'}),
];
