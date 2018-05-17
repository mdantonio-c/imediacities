import {Injectable} from '@angular/core';
import {NgbModal, NgbModalRef} from '@ng-bootstrap/ng-bootstrap';
/**
 * Servizio per la gestione delle modali
 */
@Injectable()
export class AppModaleService {

    /**
     * Mantiene il riferimento alla modale aperta
     */
    private modale: NgbModalRef;
    /*
        BELLISSIMO!!

        NgbModalOptions (rif: https://ng-bootstrap.github.io/#/components/modal/api)
            backdrop
            Whether a backdrop element should be created for a given modal (true by default).
            Alternatively, specify 'static' for a backdrop which doesn't close the modal on click.
            Type: boolean | "static"

        backdrop: 'static'
            TS2345: Argument of type '{ backdrop: string; windowClass: string; backdropClass: string; centered: boolean; keyboard: bool...' is not assignable to parameter of type 'NgbModalOptions'.
            Types of property 'backdrop' are incompatible.
            Type 'string' is not assignable to type 'boolean | "static"'.

        backdrop: 'static' as 'static'
            Ok!
    */

    /**
     * Configurazione base per le modali
     * https://ng-bootstrap.github.io/#/components/modal/api#NgbModalOptions
     * @type {{backdrop: "static"; centered: boolean; keyboard: boolean; windowClass: string}}
     */
    static conf = {
        /**
         * Determina se cliccando sulla backdrop è possible chiudere la modale (true) oppure no ('static', false)
         */
        backdrop: 'static' as 'static' ,
        /**
         * Centratura verticale della modale
         */
        centered: true,
        /**
         * Cliccando il tasto 'esc' la modale viene chiusa (true) oppure no (false)
         */
        keyboard: false,
        /**
         * Classe CSS da assegnare alla modale
         */
        windowClass: 'imc--modal'


    };

    constructor(private ngb_modal: NgbModal) {
    }

    /**
     * Ritorna il riferimento della modale correntemente aperta
     * @returns {NgbModalRef}
     */
    public get ():NgbModalRef {
        return this.modale;
    }

    /**
     * Salva il riferimento alla modale correntemente aperta
     * @param {NgbModalRef} modale - il riferimento della modale
     */
    private set (modale:NgbModalRef) {
        this.modale = modale;
    }

    /**
     * Consente di specificare la configurazione per la modale corrente
     * @param {object} conf - oggetto di configurazione per estendere AppModaleService.conf
     * @returns {}
     */
    static configura (conf = {}) {
        return Object.assign(AppModaleService.conf, conf);
    }

    /**
     * Apre una modale e ne salva il riferimento
     * @param content - contenuto della modale
     * @param conf - oggetto per estendere la configurazione base
     */
    public open (content, conf) {
        this.set(
            this.ngb_modal.open(content,AppModaleService.configura(conf))
        );
    }


}