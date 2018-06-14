import {HttpClientJsonpModule} from '@angular/common/http';
import {NguiMapModule} from '@ngui/map';

export const imports: any[] = [
    HttpClientJsonpModule,
    NguiMapModule.forRoot({apiUrl: 'https://maps.google.com/maps/api/js?libraries=places&key=AIzaSyCkSQ5V_EWELQ6UCvVGBwr3LCriTAfXypI'}),
];
