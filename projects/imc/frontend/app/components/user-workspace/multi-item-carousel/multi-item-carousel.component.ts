import { Component, OnInit, Input, Output, OnChanges, EventEmitter, ViewChild } from '@angular/core';
import { NotificationService } from '/rapydo/src/app/services/notification';
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
  @Output() onResult: EventEmitter<number> = new EventEmitter<number>();

  @ViewChild('slickModal') slickModal;

  results: ItemDetail[] = [];
  loading = false;
  private currentPage: number = 1;
  private pageSize: number = 12;

  slideConfig = {
    "infinite": false,
    "slidesToShow": 8,
    "slidesToScroll": 1,
    "swipeToSlide": true,
    "variableWidth": true,
    "lazyLoad": "progressive"
  };

  constructor(
    private catalogService: CatalogService,
    private listsService: ListsService,
    private notify: NotificationService) { }

  slickInit(e) {
    /*console.log('slick initialized');*/
  }

  breakpoint(e) {
    /*console.log('breakpoint');*/
  }

  afterChange(e) {
    /*console.log('afterChange');*/
  }

  beforeChange(e) {
    /*console.log('beforeChange');*/
  }

  ngOnInit() {
    /*this.load();*/
  }

  ngOnChanges() {
    console.log('Input changed', this.filter);
    this.load();
  }

  load() {
    this.loading = true;
    switch (this.endpoint) {
      case "lists":
        this.listsService.getLists().subscribe(
          response => {
            this.slickModal.unslick();
            this.results = response.data.map(lst => {
              return {
                'id': lst.id,
                'title': lst.attributes.name,
                'description': lst.attributes.description
              }
            });
            this.onResult.emit(this.results.length);
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
            this.slickModal.unslick();
            this.results = response["Response"].data.map(media => {
              let r = {
                'id': media.id,
                'title': MediaUtilsService.getIdentifyingTitle(media),
                'description': MediaUtilsService.getDescription(media),
                'type': media.type,
                'thumbnail': media.links['thumbnail']
              }
              if (media.type === 'aventity') r['duration'] = media.relationships.item[0].attributes.duration;
              return r;
            });

            console.log(this.results);
            this.onResult.emit(response["Meta"].totalItems);
            this.loading = false;
          },
          error => {
            this.notify.extractErrors(error.error.Response, this.notify.ERROR);
            this.loading = false;
          });
        break;
    }
  }

}