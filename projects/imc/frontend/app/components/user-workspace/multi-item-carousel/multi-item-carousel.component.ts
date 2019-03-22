import { Component, OnInit, Input, Output, OnChanges, EventEmitter, ViewChild, ChangeDetectorRef } from '@angular/core';
import { NotificationService } from '/rapydo/src/app/services/notification';
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
export class MultiItemCarouselComponent implements OnInit, OnChanges {

  @Input() filter: SearchFilter = {};
  @Input() endpoint: string = 'search';
  @Input() listId: string;
  @Output() onResult: EventEmitter<number> = new EventEmitter<number>();

  @ViewChild('slickModal') slickModal;
  @ViewChild('confirmModal') confirmModal;

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
    private cdRef : ChangeDetectorRef,
    private notify: NotificationService) { }

  slickInit(e) {
    /*console.log('slick initialized');*/
  }

  breakpoint(e) {
    console.log(e);
    /*console.log('breakpoint');*/
  }

  afterChange(e) {
    /*console.log('afterChange', e);*/

    //preventing concurrent loading
    if (!this.loading) {
      console.log(`slides size: ${this.slides.length} (in ${this.total})`);
      let slidesToShow = this.slideConfig["slidesToShow"];
      let end = e.currentSlide + slidesToShow - 1;
      console.log(`Active slides [${e.currentSlide}-${end}]`);
      let offset = 1; // load next page one step before the end
      if (this.slides.length < this.total && (end + offset) == this.slides.length) {
        this.currentPage += 1;
        this.load(true);
      }
    }
  }

  beforeChange(e) {
    /*console.log('beforeChange');*/
  }

  ngOnInit() {
    /*this.load();*/
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

  load(append = false) {
    this.loading = true;
    switch (this.endpoint) {
      case "lists":
        this.listsService.getLists().subscribe(
          response => {
            /*this.slickModal.unslick();*/
            this.slides = response.data.map(lst => {
              return {
                'id': lst.id,
                'title': lst.attributes.name,
                'description': lst.attributes.description,
                'type': lst.type
              }
            });
            /*console.log('lists', this.slides);*/
            // FIXME with pagination
            this.total = this.slides.length;
            this.onResult.emit(this.total);
            this.loading = false;
          },
          error => {
            this.notify.extractErrors(error.error.Response, this.notify.ERROR);
            this.loading = false;
          });
        break;
      case "listItems":
        this.listsService.getListItems(this.listId).subscribe(
          response => {
            this.slickModal.unslick();
            console.log(response);
            this.slides = response.data.map(media => {
              /*console.log(media);*/
              let mediaType = '';
              if (media.type === 'shot') {
                mediaType = 'aventity';
              } else {
                mediaType = (media.attributes.item_type.key === 'Video') ? 'aventity' : 'nonaventity';
              }
              let r = {
                'id': media.id,
                'title': media.title,
                'description': media.description,
                'type': mediaType,
                'thumbnail': media.links['thumbnail']
              }
              if (mediaType === 'aventity') r['duration'] = media.attributes.duration;
              return r;
            });
            this.total = this.slides.length;
            /*this.onResult.emit(response["Meta"].elements);*/
            this.loading = false;
          },
          error => {
            this.notify.extractErrors(error.error.Response, this.notify.ERROR);
            this.loading = false;
          });
        break;
      default:
        this.catalogService.search(this.filter, this.currentPage, this.pageSize, false).subscribe(
          response => {
            if (!append) {
              this.slickModal.unslick();
            }
            this.slides = this.update_results(append, this.currentPage, response["Response"].data.map(media => {
              let r = {
                'id': media.id,
                'title': MediaUtilsService.getIdentifyingTitle(media),
                'description': MediaUtilsService.getDescription(media),
                'type': media.type,
                'thumbnail': media.links['thumbnail']
              }
              if (media.type === 'aventity') r['duration'] = media.relationships.item[0].attributes.duration;
              return r;
            }));
            this.total = response["Meta"].totalItems;
            this.onResult.emit(this.total);
            this.loading = false;
          },
          error => {
            this.notify.extractErrors(error.error.Response, this.notify.ERROR);
            this.loading = false;
          });
        break;
    }
  }

  removeItem(item) {
    let itemTitle = item.title;
    item.focus = false;
    console.log(`delete item <${itemTitle}>`);
    const modalRef = this.modalService.open(this.confirmModal);
    modalRef.result.then((result) => {
      switch (item.type) {
        case "list":
          this.listsService.removeList(item.id).subscribe(
            response => {
              this.notify.showSuccess('List <' + itemTitle + '> removed successfully');
              this.load();
            },
            error => {
              this.notify.extractErrors(error.error.Response, this.notify.ERROR);
            });
          break;

        default:
          console.warn('Remove function not allowed for type', item.type);
          break;
      }
    }, (reason) => {
      // keep focus on item
      item.focus = true;
    });
  }
}