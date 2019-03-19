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
  private currentSlide: number = 0;
  private pageSize: number = 12;

  slideConfig = {
    "infinite": false,
    "slidesToShow": 8,
    "slidesToScroll": 8,
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
    console.log(e);
    /*console.log('breakpoint');*/
  }

  afterChange(e) {
    /*console.log('afterChange', e);*/

    //preventing concurrent loading
    if (!this.loading) {
      let slidesToShow = this.slideConfig["slidesToShow"];
      let end = e.currentSlide + slidesToShow - 1;

      /*console.log("You want to display from " + start + " to " + end);*/

      if (this.results.length <= end + slidesToShow) {

        this.currentPage = Math.ceil((end + 1) / slidesToShow);
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
    console.log('Input changed', this.filter);
    this.currentPage = 1;
    this.load();
  }

  update_results(append, page, new_results) {
    if (append) {
      let start = (this.currentPage -1) * this.pageSize;
      let end = start + this.pageSize - 1;

      if (this.results.length > end) {
        console.log("Results already loaded?");
      } else {
        /*console.log("Loading from " + start + " to " + end);*/

        this.results.push(...new_results);
      }
    } else {
      this.results = new_results;
    }
    return this.results
  }

  load(append=false) {
    this.loading = true;
    switch (this.endpoint) {
      case "lists":
        this.listsService.getLists().subscribe(
          response => {
            this.slickModal.unslick();
            this.results = response.data.map(lst => {
              console.log(lst);
              return {
                'id': lst.id,
                'title': lst.attributes.name,
                'description': lst.attributes.description,
                'type': lst.type
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
      case "listItems":
        /*this.listsService.getListItems()*/
        console.log('load list items...');
        this.loading = false;
        break;
      default:
        this.catalogService.search(this.filter, this.currentPage, this.pageSize, false).subscribe(
          response => {
            if (!append) {
              this.slickModal.unslick();
            }
            this.results = this.update_results(append, this.currentPage, response["Response"].data.map(media => {
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

            /*console.log(this.results);*/
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

  removeItem(item) {
    let itemTitle = item.title;
    switch (item.type) {
      case "list":
        this.listsService.removeList(item.id).subscribe(
          response => {
            this.notify.showSuccess('List <'+itemTitle+'> removed successfully');
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
    
  }

}