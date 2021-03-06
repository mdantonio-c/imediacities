import {
  Component,
  OnInit,
  OnDestroy,
  ViewChild,
  ElementRef,
  Renderer2,
  DoCheck,
} from "@angular/core";
import { Router, Route, ActivatedRoute, Params } from "@angular/router";
import { AppShotsService } from "../../services/app-shots";
import { AppMediaService } from "../../services/app-media";
import { AppModaleComponent } from "../app-modale/app-modale";
import { AppVideoPlayerComponent } from "./app-video-player/app-video-player";
import { AuthService } from "@rapydo/services/auth";
import { AppVideoService } from "../../services/app-video";
import { AppAnnotationsService } from "../../services/app-annotations";
import {
  ShotRevisionService,
  SceneCut,
} from "../../services/shot-revision.service";
import { NotificationService } from "@rapydo/services/notification";
import { MediaUtilsService } from "../../catalog/services/media-utils.service";
/**
 * Componente per la visualizzazione del media
 */
@Component({
  selector: "app-media",
  templateUrl: "app-media.html",
  providers: [ShotRevisionService],
})
export class AppMediaComponent implements OnInit, OnDestroy {
  /**
   * Riferimento al componente AppModale
   */
  @ViewChild("appModale", { static: false }) appModale: AppModaleComponent;
  /**
   * Riferimento al componente AppVideoPlayer
   */
  @ViewChild("appVideo", { static: false }) appVideo: AppVideoPlayerComponent;
  /**
   * Conteggio annotazioni
   * @type {number}
   */
  public annotations_count = 0;
  /**
   * Consente di visualizzare lo strumento per la shot revision
   */
  shot_revision_is_active: boolean = false;
  shot_revision_state: string = "";
  private shots_to_restore: any[] = [];
  /**
   * Consente di visualizzare lo strumento per la selezione multipla degli shot
   */
  public multi_annotations_is_active: boolean = false;

  /**
   * Riceve i risultati della chiamata al servizio media
   */
  public media: any;
  /**
   * Oggetto da visualizzare nel corpo della modale
   * @type {{type: string; data: {}}}
   */
  public modale = {
    /**
     * Nome del componente da visualizzare
     */
    type: "",
    /**
     * Dati da passare al componente
     */
    data: {},
  };
  /**
   * Elenco delle location da passare alla mappa
   */
  public locations;
  /**
   * Riceve i risultati della chiamata al servizio shots
   * @type {any[]}
   */
  public shots = [];
  public shots_attivi = [];
  /**
   * Lingua dell'utente da legare in futuro all'utente loggato
   * @type {string}
   */
  public user_language = "it";
  public user: any = {};
  //public type_shot: boolean;

  public media_class = "";
  public media_type = "";
  public media_id = "";
  private _subscription;

  constructor(
    private router: Router,
    private route: ActivatedRoute,
    private AuthService: AuthService,
    private Element: ElementRef,
    private AnnotationService: AppAnnotationsService,
    private MediaService: AppMediaService,
    private ShotsService: AppShotsService,
    private VideoService: AppVideoService,
    private shotRevisionService: ShotRevisionService,
    private notify: NotificationService
  ) {
    shotRevisionService.cutAdded$.subscribe((shots) => {
      this.split_shot(shots);
    });
  }

  media_type_set(url) {
    if (url.indexOf("/video") !== -1) {
      this.media_class = "page-type-video";
      this.media_type = "video";
      // this.type_shot = true;
    } else if (url.indexOf("/image") !== -1) {
      this.media_class = "page-type-image";
      this.media_type = "image";
      // this.type_shot = false;
    }
  }

  show_only_public_domain() {
    // No user logged-in
    if (this.user === null) return true;
    // The logged user has no role
    if (!this.user.roles) return true;
    // The logged user has no role
    if (Object.keys(this.user.roles).length <= 0) return true;

    // Users with special roles always see everything
    if (this.user.isAdmin) return false;
    if (this.user.isStaff) return false;
    if ("Archive" in this.user.roles) return false;
    if ("Researcher" in this.user.roles) return false;
    if ("Reviser" in this.user.roles) return false;

    // Others only see public domain
    return true;
  }
  /*
    is_public_domain() {
        let k = this.media.rights_status.key;

        // EU Orphan Work
        if (k == "02") return true;

        // In copyright - Non-commercial use permitted
        if (k == "04") return true;

        // Public Domain
        if (k == "05") return true;

        // No Copyright - Contractual Restrictions
        if (k == "06") return true;

        // No Copyright - Non-Commercial Use Only
        if (k == "07") return true;

        // No Copyright - Other Known Legal Restrictions
        if (k == "08") return true;

        // No Copyright - United States
        if (k == "09") return true;

        return false;
    }*/
  is_public_domain() {
    return this.media._item[0].public_access;
  }

  start_shot_revision() {
    this.shotRevisionService.putVideoUnderRevision(this.media_id, (error) => {
      if (error) {
        this.notify.showError(error);
        return;
      }
      let revision = {
        id: this.user.uuid,
        state: { key: "W" },
      };
      this.media._item[0]._revision = [revision];
      this.under_revision();
    });
  }

  canRevise() {
    if (this.user === null) return false;
    return (
      this.user.roles.hasOwnProperty("Reviser") &&
      this.shot_revision_is_active &&
      this.shot_revision_state != "R" &&
      this.media._item[0]._revision &&
      this.user.uuid === this.media._item[0]._revision[0].id
    );
  }

  private under_revision() {
    console.log("Revision mode activated");
    this.shot_revision_is_active = true;
    this.shot_revision_state = this.MediaService.revisionState();
    // create a copy from the actual shot list (DEEP CLONE)
    // this.shots_to_restore = $.extend(true, {}, this.shots);
    this.shots_to_restore = JSON.parse(JSON.stringify(this.shots));
  }

  exit_shot_revision() {
    this.shotRevisionService.exitRevision(this.media_id, (error) => {
      if (error) {
        this.notify.showError(error);
        return;
      }
      delete this.media._item[0]._revision;
      this.shot_revision_is_active = false;
      // shallow clone is enough here!
      this.shots = this.shots_to_restore.slice(0);
      this.shots_to_restore = [];
    });
  }

  revise_shot($event) {
    console.log("revise shot", $event);
    let op = $event.op;
    switch ($event.op) {
      case "join":
        this.join_shots($event.index - 1, $event.index);
        break;
      default:
        console.warn("Invalid operation in revising shot for " + $event.op);
    }
  }

  /**  Join two shots. */
  private join_shots(idxA, idxB) {
    let shotA = this.shots[idxA];
    let shotB = this.shots[idxB];
    shotA.duration += shotB.duration;
    shotA.end_frame_idx = shotB.end_frame_idx;
    Object.keys(shotA.annotations).forEach((e) => {
      // merge annotations
      shotA.annotations[e].push(...shotB.annotations[e]);
    });
    this.shots[idxA] = shotA;
    // remove shotB from the list
    this.shots.splice(idxB, 1);
    // update the subsequent shot numbers
    for (let i = idxA + 1; i < this.shots.length; i++) {
      this.shots[i].shot_num = this.shots[i].shot_num - 1;
    }
  }

  private split_shot(shots) {
    if (shots === undefined || shots.length != 2) {
      console.warn("Invalid input in split_shot", shots);
      this.notify.showError("Invalid input in split shot");
      return;
    }
    let next_idx = shots[0].shot_num + 1;
    this.shots.splice(next_idx, 0, shots[1]);
    this.shots[next_idx].revision_confirmed = true;
    // update the subsequent shot numbers
    for (let i = next_idx + 1; i < this.shots.length; i++) {
      this.shots[i].shot_num = this.shots[i].shot_num + 1;
    }
  }

  save_revised_shots() {
    console.log("saving revised shots...");
    if (this.shots.length === 0) {
      // should never be reached
      console.warn("Trying to save an empty revision list");
      return;
    }
    let shots: SceneCut[] = this.shots.map((s) => {
      let shot_anno_ids = [];
      for (let key in s.annotations) {
        // filter only manual anno
        // ensure unique anno ids
        shot_anno_ids.push(
          ...Array.from(
            new Set(
              s.annotations[key]
                .filter((anno) => anno.creator != null)
                .map((anno) => anno.id)
            )
          )
        );
      }
      /*console.log('current annotations for shot_num ' + s.shot_num, shot_anno_ids);*/
      return {
        shot_num: s.shot_num,
        cut: s.start_frame_idx,
        confirmed: s.revision_confirmed,
        double_check: s.revision_check,
        annotations: shot_anno_ids,
      } as SceneCut;
    });
    this.shotRevisionService.reviseVideoShots(this.media_id, shots, () => {
      this.shot_revision_state = "R";
      this.notify.showSuccess("Your request has been successfully submitted");
    });

    // because the shot list size could have changed then update the list of 'shot_attivi'
    this.shots_attivi = this.shots.map((s) => false);
  }

  /**
   * Modifica la visibilità dello strumento per la shot revision
   */
  shot_revision_toggle() {
    this.shot_revision_is_active = !this.shot_revision_is_active;
  }

  /**
   * Modifica la visibilità dello strumento per la selezione multipla degli shot
   * e ne resetta lo stato deselezionando tutti
   */
  multi_annotations_toggle() {
    this.multi_annotations_is_active = !this.multi_annotations_is_active;
    this.shots_attivi_reset();
  }

  /**
   * Apre una modale visualizzando al suo interno il compontente coi dati ricevuti
   * @param componente Configurazione del componente daq visualizzare nella modale
   */
  modal_show(componente) {
    //  fermo il video principale
    if (this.appVideo) {
      this.appVideo.video.pause();
    }
    this.modale.type = componente.modale;
    if (componente.previous) {
      // use the previous flag to add the previous shot to the list
      let previous_shot_num = componente.data.shots.slice(-1)[0].shot_num - 1;
      componente.data.shots.unshift(this.shots[previous_shot_num]);
    }
    this.modale.data = componente.data;
    this.appModale.open(
      componente.titolo,
      this.MediaService.type(),
      componente.classe
    );
  }

  /**
   * Apre una modale visualizzando al suo interno il componente coi dati ricevuti
   * Inserisce nei dati da visualizzare gli shots selezionati
   * @param evento Evento richiamante
   * @param componente Componente selezionato
   */
  modal_show_multi(evento, componente) {
    let data = this.shots_attivi.reduce((acc, value, index) => {
      if (value) {
        acc.push(this.shots[index]);
      }
      return acc;
    }, []);
    //console.log('modal_show_multi: data=',data);
    if (!data.length) return;

    let comp = {
      modale: componente,
      data: {
        shots: data,
      },
      titolo: evento.target.innerText,
    };
    this.modal_show(comp);
  }

  shot_selezionato(evento) {
    this.shots_attivi[evento.index] = evento.stato;
  }

  shots_attivi_reset() {
    this.shots_attivi = this.shots_attivi.map((s) => false);
  }

  shots_init(shots) {
    //  Questo tipo di aggiornamento serve per non
    //   ridisegnare tutti i componenti collegati agli shots
    if (this.shots.length) {
      this.shots.forEach((s, idx) => {
        s.annotations = shots[idx].annotations;
      });
    } else {
      this.shots = shots;
    }
    // se shots_attivi non è vuoto allora non
    //  lo voglio resettare, potrebbe contenere
    //  le info sugli shot selezionati per la annotaz multipla
    if (this.shots_attivi.length == 0) {
      this.shots_attivi = shots.map((s) => false);
    }
  }

  shots_update(evento) {
    if (this.media_type === "video") {
      this.ShotsService.get();
    } else if (this.media_type === "image") {
      this.AnnotationService.get(this.media_id, "images");
    }
  }

  video_player_set(event) {
    this.VideoService.video_set(event);
  }

  media_entity_normalize(mediaEntity) {
    //  Normalizzo i dati delle immagini
    if (this.media_type === "image") {
      // anno di produzione
      if (mediaEntity.date_created) {
        mediaEntity.production_years = mediaEntity.date_created;
      }
      // titolo principale
      mediaEntity.identifying_title = MediaUtilsService.getIdentifyingTitle(
        mediaEntity
      );
      this.locations = [];
    }

    //  elimino i titoli aggiuntivi se sono identici a quello identificativo
    if (mediaEntity._titles.length) {
      mediaEntity._titles = mediaEntity._titles.filter(
        (t) => t.text !== mediaEntity.identifying_title
      );
    }

    return mediaEntity;
  }

  /**
   * Esegue le richieste del video e degli shot
   */
  ngOnInit() {
    this.user = this.AuthService.getUser();
    this.media_type_set(this.router.url);

    this._subscription = this.route.params.subscribe((params: Params) => {
      this.media_id = params["uuid"];
      let endpoint =
        this.router.url.indexOf("videos") != -1 ? "videos" : "images";

      this.MediaService.get(this.media_id, endpoint, (mediaEntity) => {
        this.media = this.media_entity_normalize(mediaEntity);

        // To be confirmed
        setTimeout(() => {
          let tabs = this.Element.nativeElement.querySelector(
            "#pills-tab > li"
          );
          if (tabs) tabs.click();
        }, 100);

        if (this.media_type === "video") {
          this.ShotsService.get(this.media_id, endpoint);
        }

        if (this.media_type === "image") {
          this.AnnotationService.get(this.media_id, endpoint);
          const annotations_subscription = this.AnnotationService.update.subscribe(
            (annotations) => {
              this.ShotsService.get(this.media_id, endpoint, {
                annotations: annotations,
                links: this.media.links,
                item_id: this.media._item[0].id,
              });
            }
          );
          this._subscription.add(annotations_subscription);
        }

        const shots_subscription = this.ShotsService.update.subscribe(
          (shots) => {
            this.shots_init(shots);
            const annotations = this.ShotsService.annotations();
            this.annotations_count = annotations.length;
            if (this.user !== null) {
              this.locations = annotations.filter(
                (a) => a.group === "location"
              );
            }
            if (this.media._item[0]._revision) {
              this.under_revision();
            }
          }
        );
        this._subscription.add(shots_subscription);
      });
    });
  }

  ngOnDestroy() {
    this._subscription.unsubscribe();
  }
}
