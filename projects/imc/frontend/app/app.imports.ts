import { NguiMapModule} from '@ngui/map';

export const imports: any[] = [
  NguiMapModule.forRoot({apiUrl: 'https://maps.google.com/maps/api/js?key=MY_GOOGLE_API_KEY'}),
];