export interface CustomUser {
  readonly declared_institution: string;
}

export interface File {
  creation: number;
  modification: number;
  name: string;
  size: number;
  type: string;
  status: string;
  status_message?: string;
  /** @nullable */
  task_id?: string;
  /** @nullable */
  warnings?: string;
}

export interface Files extends Array<File> {}

export interface Entity {
  id: string;
  created: Date;
  modified: Date;
  type: string;
}

export interface UserListEntity extends Entity {
  name: string;
  description: string;
  /** @nullable */
  nb_items?: number;
}

export interface SearchResponse {
  data: any[];
  meta: MetaSearchResponse;
}

export interface MetaSearchResponse {
  totalItems: number;
  countByProviders: number;
  countByYears: number;
}

export interface GeoTag {
  iri: string;
  name: string;
  spatial: [number, number];
}

export interface GeoDistanceAnnotation extends GeoTag {
  distance: number;
  sources: MediaContent[];
}

export interface MediaContent {
  uuid: string;
  external_ids: string[];
  rights_status: string;
  title: string;
  type: string;
  year: string;
}

export interface Annotation {
  creator_type: string;
  description: string;
  group: string;
  iri?: string;
  id?: string;
  name?: string;
  label?: MultiLanguageLabel;
  source: string;
}

export interface MultiLanguageLabel {
  // mandatory lang
  en: string;
  // any other lang
  [key: string]: string;
}
