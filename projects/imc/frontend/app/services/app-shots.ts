import { Injectable, Output, EventEmitter } from "@angular/core";

import { ApiService } from "@rapydo/services/api";
import { NotificationService } from "@rapydo/services/notification";

@Injectable()
export class AppShotsService {
  private _annotations_all: IMC_Annotation[] = [];
  private _annotations_map = new Map();
  private _media_id = "";
  private _shots: IMC_Shot[] = [];
  private _tags_all: IMC_Tag[] = [];
  private _tags_map = new Map();

  @Output() update: EventEmitter<any> = new EventEmitter();
  private _others_data_as_object;

  constructor(private api: ApiService, private notify: NotificationService) {}

  /**
   * Ottiene gli shots del video media_id
   * @param media_id
   * @param endpoint
   * @param others_data_as_object
   */
  get(media_id?, endpoint?, others_data_as_object?) {
    if (!media_id) {
      media_id = this._media_id;
    }

    //  Quando l'applicazione non è di tipo video non chiamo shots, ma li simulo.
    if (endpoint && endpoint !== "videos") {
      const shot_mimic = [
        {
          id: others_data_as_object.item_id,
          links: others_data_as_object.links,
          shot_num: 0,
          annotations: others_data_as_object.annotations,
        },
      ];

      this._media_id = media_id;
      this._shots_parse(shot_mimic, "image");
      this.update.emit(this._shots);
      return;
    }

    this.api.get(endpoint || "videos", `${media_id}/shots`).subscribe(
      (response) => {
        this._media_id = media_id;
        this._shots_parse(response, "video");
        this.update.emit(this._shots);
      },
      (error) => {
        this.notify.showError(error);
      }
    );
  }
  media_id() {
    return this._media_id;
  }
  /**
   * Ritorna gli shots processati
   * @returns {IMC_Shot[]}
   */
  shots(): IMC_Shot[] {
    return this._shots;
  }
  /**
   * Verifica se l'annotazione annotation esiste nello shot shot
   * @param shot
   * @param annotation
   * @returns {boolean}
   */
  shot_has_annotation(shot, annotation) {
    let found = 0;
    for (let key in shot.annotations) {
      if (shot.annotations[key].length) {
        found += shot.annotations[key].filter((s) => s.id === annotation.id)
          .length;
      }
    }
    return found > 0;
  }

  shot_has_tag(shot, tag) {
    let found = 0;
    for (let key in shot.annotations) {
      if (shot.annotations[key].length) {
        if (tag.id != null) {
          found += shot.annotations[key].filter((s) => s.iri === tag.id).length;
        } else {
          found += shot.annotations[key].filter((s) => s.name === tag.name)
            .length;
        }
      }
    }
    return found > 0;
  }
  /**
   * Ritorna un oggetto con tutte le annotazioni ordinate alfabeticamente
   * @returns {IMC_Annotation[]}
   */
  annotations(): IMC_Annotation[] {
    return this._annotations_all;
  }

  /**
   * Ritorna un oggetto con tutti tag ordinati alfabeticamente
   * @returns {IMC_Tag[]}
   */
  tags(): IMC_Tag[] {
    return this._tags_all;
  }

  /**
   * Filtra le annotazioni in base al filtro passato
   * @param array_da_filtrare
   * @param filtro
   * @param {string} proprieta - proprietà di annotation su cui testare il filtro
   * @param {string} re_flags
   * @returns {IMC_Annotation[]}
   */
  annotations_filter(
    array_da_filtrare,
    filtro,
    proprieta = "name",
    re_flags = "i"
  ): IMC_Annotation[] {
    if (!array_da_filtrare) {
      array_da_filtrare = this._annotations_all.slice();
    }

    filtro = new RegExp(filtro, re_flags);
    return array_da_filtrare.filter((annotation) =>
      filtro.test(annotation[proprieta])
    );
  }
  /**
   * Processa gli shot
   * ne estrae proprietà e annotazioni
   * ritornando l'elenco degli shot elaborato
   * @param shots
   * @param media_type
   * @returns {IMC_Shot[]}
   * @private
   */
  private _shots_parse(shots, media_type): IMC_Shot[] {
    let shots_processed = [];
    //  per ogni shot
    shots.forEach((s, index) => {
      let shot_processato: IMC_Shot = {
        id: s.id,
        shot_num: s.shot_num,
        timestamp: s.timestamp,
        duration: s.duration,
        revision_confirmed: s.revision_confirmed,
        revision_check: s.revision_check,
        end_frame_idx: s.end_frame_idx,
        start_frame_idx: s.start_frame_idx,
        links: s.links,
        annotations: {
          locations: [],
          tags: [],
          notes: [],
          references: [],
          links: [],
        },
      };
      //  processo annotazioni
      this._annotations_parse(
        shot_processato.annotations,
        s.annotations,
        media_type,
        index
      );
      AppShotsService._annotations_sort(shot_processato.annotations);
      shots_processed.push(shot_processato);
    });
    this._shots = shots_processed;
    this._annotations_all_from_map();
    this._tags_all_from_map();
    return this.shots();
  }
  /**
   * Processa le annotazioni suddividendole per categoria
   * @param target
   * @param annotations
   * @param media_type
   * @param shot_indice shot in cui compare l'annotazione
   * @private
   */
  private _annotations_parse(target, annotations, media_type, shot_indice) {
    annotations.forEach((annotation) => {
      //  Term tag e locations
      if (annotation.annotation_type.key === "TAG") {
        annotation.bodies.forEach((body) => {
          let tipo = "tags";
          if (body.spatial !== null && typeof body.spatial === "object") {
            tipo = "locations";
          }
          this._annotation_add(
            target[tipo],
            this._annotation_set(annotation, body, media_type),
            shot_indice
          );
        });
        //  Note
      } else if (annotation.annotation_type.key === "DSC") {
        this._annotation_add(
          target.notes,
          this._annotation_set(annotation, annotation.bodies[0], media_type),
          shot_indice
        );
        // Link
      } else if (annotation.annotation_type.key === "LNK") {
        let body_linked = annotation.bodies[0];
        if (body_linked.type == "textualbody") {
          // external link
          this._annotation_add(
            target.links,
            this._annotation_set(annotation, annotation.bodies[0], media_type),
            shot_indice
          );
        } else if (body_linked.type == "bibliographicreference") {
          // bibliographic references
          this._annotation_add(
            target.references,
            this._annotation_set(annotation, annotation.bodies[0], media_type),
            shot_indice
          );
        } else {
          // TODO add internal link to shot/item/(?)
        }
      }
    });
  }
  /**
   * Aggiunge l'annotazione annotation all'array target
   * e aggiunge l'annotazione all'elenco generale gestendone il conteggio e l'elenco degli shot in cui appare
   * @param target
   * @param annotation
   * @param shot_indice Shot in cui compare l'annotazione
   * @private
   */
  private _annotation_add(target, annotation, shot_indice) {
    annotation.shots_idx = [shot_indice];
    target.push(annotation);

    // add annotation to annotation_from_map
    if (this._annotations_map.has(annotation.id)) {
      let annotation_from_map = this._annotations_map.get(annotation.id);
      annotation_from_map.count += 1;
      annotation_from_map.shots_idx.push(shot_indice);
    } else {
      annotation.count = 1;
      annotation.shots_idx = [shot_indice];
      this._annotations_map.set(annotation.id, annotation);
    }
    // add tags to tag_from_map
    if (annotation.type === "TAG") {
      let iri =
        annotation.iri != null ? annotation.iri : "textual:" + annotation.name;
      if (this._tags_map.has(iri)) {
        let tag = this._tags_map.get(iri);
        tag.count += 1;
        tag.shots_idx.push(shot_indice);
      } else {
        this._tags_map.set(iri, {
          id: annotation.iri,
          name: annotation.name,
          count: 1,
          group: annotation.group,
          shots_idx: [shot_indice],
        });
      }
    }
  }
  private _annotations_all_from_map() {
    this._annotations_all = Array.from(this._annotations_map).map(
      (annotation) => annotation[1]
    );
    this._annotations_all.sort(AppShotsService._sort_alpha);
    this._annotations_map.clear();
  }
  private _tags_all_from_map() {
    this._tags_all = Array.from(this._tags_map).map((tag) => tag[1]);
    this._tags_all.sort(AppShotsService._sort_alpha);
    this._tags_map.clear();
  }
  private _decode_language(lang): string {
    let language;
    switch (lang) {
      case "ca":
        language = "Català";
        break;
      case "da":
        language = "Dansk";
        break;
      case "de":
        language = "Deutsche";
        break;
      case "en":
        language = "English";
        break;
      case "es":
        language = "Español";
        break;
      case "fr":
        language = "Français";
        break;
      case "it":
        language = "Italiano";
        break;
      case "nl":
        language = "Nederlands";
        break;
      case "sv":
        language = "Svenska";
        break;
      case "el":
        language = "Ελληνικά";
        break;
      default:
        language = "";
        break;
    }

    return language;
  }
  /**
   * Crea un'annotazione riorganizzando i dati
   * @param annotation
   * @param annotation_body
   * @param media_type
   * @returns {IMC_Annotation}
   * @private
   */
  private _annotation_set(
    annotation,
    annotation_body,
    media_type
  ): IMC_Annotation {
    let name,
      group,
      language = null;
    if (annotation_body.type === "textualbody") {
      name = annotation_body.value;
      group = annotation.type === "TAG" ? "term" : null;
      if (annotation_body.language) {
        language = this._decode_language(annotation_body.language);
      }
    } else if (annotation_body.type === "resourcebody") {
      name = annotation_body.name;
      group = annotation_body.spatial ? "location" : "term";
    } else if (annotation_body.type === "bibliographicreference") {
      name = annotation_body.type;
      group = "reference";
    } else {
      console.warn("Cannot extract name and group from annotation_body");
      name = "";
      group = "";
    }
    return {
      creation_date: annotation.creation_datetime,
      creator: annotation.creator ? annotation.creator.id : null,
      creator_type: annotation.creator ? annotation.creator.type : null,
      embargo: annotation.embargo || null,
      group: group,
      body_id: annotation_body.id,
      id: annotation.id,
      iri: annotation_body.iri || null,
      name: name,
      private: annotation.private || false,
      language: language || "",
      spatial: annotation_body.spatial || null,
      type: annotation.annotation_type.key,
      source: media_type,
      source_uuid: this._media_id,
      reference:
        annotation_body.type === "bibliographicreference"
          ? annotation_body.attributes
          : null,
    };
  }

  /**
   * Ordina alfabeticamente le annotazioni
   * @param target
   * @private
   */
  static _annotations_sort(target) {
    for (let key in target) {
      if (target[key].length) {
        target[key].sort(AppShotsService._sort_alpha);
      }
    }
  }

  /**
   * Ordinamento alfabetico
   * @param a
   * @param b
   * @returns {number}
   * @private
   */
  static _sort_alpha(a, b) {
    if (a.name.toLowerCase() < b.name.toLowerCase()) return -1;
    if (a.name.toLowerCase() > b.name.toLowerCase()) return 1;
    return 0;
  }
}

export interface IMC_Annotation {
  creation_date: Date;
  creator: string;
  creator_type: string;
  embargo: Date;
  group: string;
  body_id: string;
  id: string;
  iri: string;
  name: string;
  private: boolean;
  language: string;
  spatial: number[];
  type: string;
  source: string;
  source_uuid: string;
  reference?: BibliographicReference;
}

export interface IMC_Shot {
  id: string;
  shot_num: number;
  timestamp: string;
  duration: number;
  revision_confirmed: boolean;
  revision_check: boolean;
  end_frame_idx: number;
  start_frame_idx: number;
  links: {};
  annotations: {
    locations: IMC_Annotation[];
    tags: IMC_Annotation[];
    notes: IMC_Annotation[];
    references: IMC_Annotation[];
    links: IMC_Annotation[];
  };
}

export interface IMC_Tag {
  id: string;
  name: string;
  group: string;
  count: number;
  shots_idx: number[];
}

export interface BibliographicReference {
  title: string;
  authors: string[];
  book_title?: string;
  journal?: string;
  volume?: string;
  number?: string;
  year?: number;
  month?: number;
  editor?: string;
  publisher?: string;
  address?: string;
  url?: string;
  isbn?: string;
  doi?: string;
}
