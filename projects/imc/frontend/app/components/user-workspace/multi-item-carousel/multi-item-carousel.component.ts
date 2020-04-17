import { Component, Input, Output, OnChanges, EventEmitter, ViewChild, ChangeDetectorRef } from '@angular/core';
import { NotificationService } from '@rapydo/services/notification';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { Providers } from '../../../catalog/services/data';
import { MediaUtilsService } from '../../../catalog/services/media-utils.service'
import { CatalogService, SearchFilter } from '../../../catalog/services/catalog.service';
import { ListsService } from '../../../services/lists.service'
import { ItemDetail } from '../item-detail/item-detail.component';

@Component({
  selector: 'multi-item-carousel',
  templateUrl: './multi-item-carousel.component.html',
  styleUrls: ['./multi-item-carousel.component.css'],
})
export class MultiItemCarouselComponent implements OnChanges {

  @Input() filter: SearchFilter = {};
  @Input() endpoint: string = 'search';
  @Input() listId: string;
  @Output() onResult: EventEmitter<number> = new EventEmitter<number>();
  @Output() onDelete: EventEmitter<string> = new EventEmitter<string>();

  @ViewChild('slickModal', { static: false }) slickModal;
  @ViewChild('confirmModal', { static: false }) confirmModal;
  @ViewChild('itemConfirmModal', { static: false }) itemConfirmModal;

  slides: ItemDetail[] = [];
  loading = false;
  private currentPage: number = 1;
  private currentSlide: number = 0;
  private pageSize: number = 10; // pageSize MUST be greater than slidesToShow
  private total: number;

  slideConfig = {
    "infinite": false,
    "slidesToShow": 8,
    "slidesToScroll": 1,
    "swipeToSlide": true,
    "variableWidth": true,
    "lazyLoad": "progressive"
  };

  _trackBy(slide) {
    return slide.id;
  }

  constructor(
    private catalogService: CatalogService,
    private listsService: ListsService,
    private modalService: NgbModal,
    private cdRef: ChangeDetectorRef,
    private notify: NotificationService) { }

  slickInit(e) {
    /*console.log('slick initialized');*/
  }

  breakpoint(e) {
    /*console.log('breakpoint', e);*/
  }

  afterChange(e) {
    /*console.log('afterChange', e);*/

    //preventing concurrent loading
    if (!this.loading) {
      /*console.log(`slides size: ${this.slides.length} (in ${this.total})`);*/
      let slidesToShow = this.slideConfig["slidesToShow"];
      let end = e.currentSlide + slidesToShow - 1;
      /*console.log(`Active slides [${e.currentSlide}-${end}]`);*/
      let offset = 1; // load next page one step before the end
      if (this.slides.length < this.total && (end + offset) == this.slides.length) {
        this.currentPage += 1;
        this.load(true);
      }
    }
  }

  beforeChange(e) {
    /*console.log('beforeChange', e);*/
  }

  ngOnChanges() {
    /*console.log('Input changed', this.filter);*/
    this.currentPage = 1;
    this.load();
  }

  update_results(append, page, new_results) {
    if (append) {
      let start = (this.currentPage - 1) * this.pageSize;
      let end = start + this.pageSize - 1;

      if (this.slides.length > end) {
        console.log("Results already loaded?");
      } else {
        /*console.log("Loading from " + start + " to " + end);*/
        this.slides.push(...new_results);
      }
    } else {
      this.slides = new_results;
    }
    return this.slides
  }

  close() {
    this.slides = [];

    if (this.slickModal !== undefined) {
      this.slickModal.unslick();
    }
  }

  load(append = false) {
    this.loading = true;
    switch (this.endpoint) {
      case "lists":
        /*console.log('load my list...');*/
        this.close();
        this.listsService.getLists(undefined, true).subscribe(
          response => {
            this.slickModal.unslick();
            this.slides = response.map(lst => {
              return {
                'id': lst.id,
                'title': lst.name,
                'description': lst.description,
                'type': lst.type,
                'nb_items': lst.nb_items
              }
            });
            this.total = this.slides.length;
            this.onResult.emit(this.total);
            this.loading = false;
          },
          error => {
            this.notify.showError(error);
            this.loading = false;
            this.slickModal.initSlick();
          });
        break;
      case "listItems":
        console.log(`load items for list <${this.listId}>`);
        /*this.slides = [];
        this.slickModal.unslick();*/
        this.close();
        this.listsService.getListItems(this.listId).subscribe(
          response => {
            this.slides = response.map(media => {
              let mediaType = '';
              if (media.type === 'shot') {
                mediaType = 'aventity';
              } else {
                mediaType = (media.item_type.key === 'Video') ? 'aventity' : 'nonaventity';
              }
              let r = {
                'id': media.id,
                'title': media.title,
                'description': media.description,
                'type': mediaType,
                'thumbnail': media.links['thumbnail'],
                'listItem': true,
                'listId': this.listId,
                'ref': media
              }
              if (mediaType === 'aventity') r['duration'] = media.duration;
              return r;
            });
            this.total = this.slides.length;
            this.onResult.emit(this.total);
            this.loading = false;
          },
          error => {
            this.notify.showError(error);
            this.loading = false;
          });
        break;
      default:
        if (!append) {
          this.close();
        }
        /*console.log(this.filter);*/
        this.catalogService.search(this.filter, this.currentPage, this.pageSize, false).subscribe(
          response => {
            this.slides = this.update_results(append, this.currentPage, response.data.map(media => {
              let r = {
                'id': media.id,
                'title': MediaUtilsService.getIdentifyingTitle(media),
                'description': MediaUtilsService.getDescription(media),
                'type': media.type,
                'thumbnail': media.links['thumbnail']
              }
              if (media.type === 'aventity') r['duration'] = media._item[0].duration;
              return r;
            }));
            this.total = response.meta.totalItems;
            this.onResult.emit(this.total);
            this.loading = false;
            /*this.slickModal.initSlick();*/
          },
          error => {
            this.notify.showError(error);
            this.loading = false;
          });
        break;
    }
  }

  removeItem(item) {
    let itemTitle = item.title;
    item.focus = false;
    if (item.listItem) {
      console.log(`remove item <${itemTitle}> from list <${item.listId}>`);
      this.modalService.open(this.itemConfirmModal).result.then(
        (result) => {
          this.listsService.removeItemfromList(item.id, item.listId).subscribe(
            response => {
              this.notify.showSuccess(`Item <${itemTitle}> removed successfully`);
              this.slides = this.slides.filter(s =>  s.id !== item.id);
              this.total = this.slides.length;
              this.onResult.emit(this.total);
              if (this.total === 0) {
                this.slickModal.unslick();
              }
            },
            error => {
              this.notify.showError(error);
            });
        }, (reason) => {
          // keep focus on item
          item.focus = true;
        });
      return;
    }

    const modalRef = this.modalService.open(this.confirmModal);
    modalRef.result.then((result) => {
      switch (item.type) {
        case "list":
          console.log(`delete list <${itemTitle}>`);
          this.listsService.removeList(item.id).subscribe(
            response => {
              this.notify.showSuccess(`List <${itemTitle}> removed successfully`);
              // update the list in the view
              this.slides = this.slides.filter(s =>  s.id !== item.id);
              this.total = this.slides.length;
              this.onResult.emit(this.total);
              if (this.total === 0) {
                this.slickModal.unslick();
              }
              // close the related item list if open
              this.onDelete.emit(item.id);
            },
            error => {
              this.notify.showError(error);
            });
          break;

        default:
          console.warn(`Delete operation not allowed for type ${item.type}`);
          break;
      }
    }, (reason) => {
      // keep focus on item
      item.focus = true;
    });
  }
}