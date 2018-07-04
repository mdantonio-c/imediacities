import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { SearchThumbnailComponent } from './search-thumbnail.component';

describe('SearchThumbnailComponent', () => {
  let component: SearchThumbnailComponent;
  let fixture: ComponentFixture<SearchThumbnailComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ SearchThumbnailComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(SearchThumbnailComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
