import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'multi-item-carousel',
  templateUrl: './multi-item-carousel.component.html',
  styleUrls: ['./multi-item-carousel.component.css'],
})
export class MultiItemCarouselComponent implements OnInit {
  images = [1, 2, 3, 4, 5, 6, 7, 8, 9].map(() => `https://picsum.photos/900/500?random&t=${Math.random()}`);
  games= [{"title_id":1,"title_name":"MIssion Impossible","title_img":"https://media.services.cinergy.ch/media/box1600/f1323e57a2c4ea79dde779a89d561f85bfbe6bf5.jpg","genres":[{"id":1,"name":"Action"},{"id":2,"name":"Adventure"}]},{"title_id":2,"title_name":"Matrix","title_img":"https://www.sideshowtoy.com/assets/products/903302-neo/lg/the-matrix-neo-sixth-scale-figure-hot-toys-903302-01.jpg","genres":[{"id":1,"name":"Action"},{"id":2,"name":"Adventure"},{"id":6,"name":"Fantasy"}]},{"title_id":3,"title_name":"Avengers","title_img":"http://media.comicbook.com/2018/03/avengers-infinity-war-poster-all-iron-man-version-1096449.jpeg","genres":[{"id":1,"name":"Action"},{"id":2,"name":"Adventure"},{"id":6,"name":"Fantasy"}]},{"title_id":4,"title_name":"Stargate SG-1","title_img":"https://image.tmdb.org/t/p/w300_and_h450_bestv2/rst5xc4f7v1KiDiQjzDiZqLtBpl.jpg","genres":[{"id":1,"name":"Action"},{"id":5,"name":"Drama"},{"id":2,"name":"Adventure"},{"id":9,"name":"Sci Fi"}]},{"title_id":5,"title_name":"Scooby Doo","title_img":"https://images-na.ssl-images-amazon.com/images/G/01/aplusautomation/vendorimages/1cdd3ea2-f14f-416b-9aaa-644a9a01ad8c.jpg._CB321085566_.jpg","genres":[{"id":1,"name":"Action"},{"id":10,"name":"Thriller"},{"id":6,"name":"Fantasy"}]}];
  cards = [
    {
      title: 'Bologna monumentale',
      description: "Le vedute di Bologna riprodotte in questa pellicola sono molte e svariate. Dapprima è un grande panorama della città, preso dall'altura di San Michele in Bosco. Vengono poi le porte principale: porta Galliera presso la stazione Ferroviaria, porta San Donato ... e porta Saragozza, ricostruita nel 1859 a foggia di fortilizio. seguono varie vedute dei caratteristici portici di Bologna, che fiancheggiano le vie anche meno frequentate...",
      type: 'Video',
      img: 'http://localhost:8080/api/videos/09a6f13f-7f0b-4674-a6e8-49dbecbf58c0/content?type=thumbnail'
    },
    {
      title: 'Card Title 2',
      description: 'Some quick example text to build on the card title and make up the bulk of the card content',
      buttonText: 'Button',
      img: 'https://mdbootstrap.com/img/Photos/Horizontal/Nature/4-col/img%20(34).jpg'
    },
    {
      title: 'Card Title 3',
      description: 'Some quick example text to build on the card title and make up the bulk of the card content',
      buttonText: 'Button',
      img: 'https://mdbootstrap.com/img/Photos/Horizontal/Nature/4-col/img%20(34).jpg'
    },
    {
      title: 'Card Title 4',
      description: 'Some quick example text to build on the card title and make up the bulk of the card content',
      buttonText: 'Button',
      img: 'https://mdbootstrap.com/img/Photos/Horizontal/Nature/4-col/img%20(34).jpg'
    },
    {
      title: 'Card Title 5',
      description: 'Some quick example text to build on the card title and make up the bulk of the card content',
      buttonText: 'Button',
      img: 'https://mdbootstrap.com/img/Photos/Horizontal/Nature/4-col/img%20(34).jpg'
    },
    {
      title: 'Card Title 6',
      description: 'Some quick example text to build on the card title and make up the bulk of the card content',
      buttonText: 'Button',
      img: 'https://mdbootstrap.com/img/Photos/Horizontal/Nature/4-col/img%20(34).jpg'
    },
    {
      title: 'Card Title 7',
      description: 'Some quick example text to build on the card title and make up the bulk of the card content',
      buttonText: 'Button',
      img: 'https://mdbootstrap.com/img/Photos/Horizontal/Nature/4-col/img%20(34).jpg'
    },
    {
      title: 'Card Title 8',
      description: 'Some quick example text to build on the card title and make up the bulk of the card content',
      buttonText: 'Button',
      img: 'https://mdbootstrap.com/img/Photos/Horizontal/Nature/4-col/img%20(34).jpg'
    },
    {
      title: 'Card Title 9',
      description: 'Some quick example text to build on the card title and make up the bulk of the card content',
      buttonText: 'Button',
      img: 'https://mdbootstrap.com/img/Photos/Horizontal/Nature/4-col/img%20(34).jpg'
    },
  ];
  slides: any = [[]];
  chunk(arr, chunkSize) {
    let R = [];
    for (let i = 0, len = arr.length; i < len; i += chunkSize) {
      R.push(arr.slice(i, i + chunkSize));
    }
    return R;
  }
  ngOnInit() {
    this.slides = this.chunk(this.cards, 3);
  }
}