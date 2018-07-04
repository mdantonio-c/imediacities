export interface MediaEntity {
	attributes: EntityAttributes;
	id: string;
	relationships: any;
}

export interface EntityAttributes {
	collection_title: string;
	external_ids: string[];
	identifying_title: string;
	identifying_title_origin: string;
	production_years: string[];
	rights_status: RightsStatus;
	view_filmography: string;
}

export interface RightsStatus {
	description: string;
	key: string;
}

export const IPRStatuses = [{
	"code": "01",
	"name": "In copyright"
}, {
	"code": "02",
	"name": "EU Orphan Work"
}, {
	"code": "03",
	"name": "In copyright - Educational use permitted"
}, {
	"code": "04",
	"name": "In copyright - Non-commercial use permitted"
}, {
	"code": "05",
	"name": "Public Domain"
}, {
	"code": "06",
	"name": "No Copyright - Contractual Restrictions"
}, {
	"code": "07",
	"name": "No Copyright - Non-Commercial Use Only"
}, {
	"code": "08",
	"name": "No Copyright - Other Known Legal Restrictions"
}, {
	"code": "09",
	"name": "No Copyright - United States"
}, {
	"code": "10",
	"name": "Copyright Undetermined"
}];

export const Providers = [{
	"code": "CCB",
	"name": "CCB - Cineteca di Bologna",
	"city": {
		// Bologna, Italy
		"position": [44.494887, 11.3426162],
		"name": "Bologna"
	}
}, {
	"code": "CRB",
	"name": "CRB - Cinematheque Royale de Belgique",
	"city": {
		// Brussels, Belgium
		"position": [50.8503463, 4.3517211],
		"name": "Brussels"
	}
}, {
	"code": "DFI",
	"name": "DFI - Det Danske Filminstitut",
	"city": {
		// Copenhagen, Denmark
		"position": [55.6760968, 12.568337199999974],
		"name": "Copenhagen"
	}
}, {
	"code": "DIF",
	"name": "DIF - Deutsches Filminstitut",
	"city": {
		// Frankfurt am Main, German
		"position": [50.1109221, 8.682126700000026],
		"name": "Frankfurt am Main"
	}
}, {
	"code": "FDC",
	"name": "FDC - Filmoteca de Catalunya",
	"city": {
		// Barcelona, Spain
		"position": [41.3850639, 2.1734034999999494],
		"name": "Barcelona"
	}
}, {
	"code": "MNC",
	"name": "MNC - Museo Nazionale del Cinema",
	"city": {
		// Turin, Italy
		"position": [45.070312, 7.686856499999976],
		"name": "Turin"
	}
}, {
	"code": "OFM",
	"name": "OFM - Österreichisches Filmmuseum",
	"city": {
		// Vienna, Austria
		"position": [48.2081743, 16.37381890000006],
		"name": "Vienna"
	}
}, {
	"code": "SFI",
	"name": "SFI - Svenska Filminstitutet",
	"city": {
		// Stockholm, Sweden
		"position": [59.32932349999999, 18.068580800000063],
		"name": "Stockholm"
	}
}, {
	"code": "TTE",
	"name": "TTE - Greek Film Archive",
	"city": {
		// Athens, Greece
		"position": [37.9838096, 23.727538800000048],
		"name": "Athens"
	}
}];