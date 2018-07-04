import {Pipe, PipeTransform} from '@angular/core';

@Pipe({
    name: 'providerToCity'
})
export class ProviderToCityPipe implements PipeTransform {

    private truthy = [true, '^s[i|ì|Ì]?$'];
    private _test = function (value, item) {

        if (typeof item === 'boolean') {
            return item === value;
        } else {
            return new RegExp(item, 'i').test(value);
        }
    };

    transform(provider: any): any {

        if (provider) {
            provider = provider.toUpperCase();
        }

        if (provider === 'CCB') return 'Bologna';
        else if (provider === 'CRB') return 'Brussels';
        else if (provider === 'DFI') return 'Copenhagen';
        else if (provider === 'DIF') return 'Frankfurt am Main';
        else if (provider === 'FDC') return 'Barcelona';
        else if (provider === 'MNC') return 'Turin';
        else if (provider === 'OFM') return 'Vienna';
        else if (provider === 'SFI') return 'Stockholm';
        else if (provider === 'TTE') return 'Athens';
        else return provider;
    }

}