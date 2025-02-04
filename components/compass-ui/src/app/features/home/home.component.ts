import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { CarouselModule } from 'primeng/carousel';
import { ProgressSpinnerModule } from 'primeng/progressspinner';
import { MessageModule } from 'primeng/message';
import { InputTextModule } from 'primeng/inputtext';
import { SolutionService } from '../../core/services/solution.service';
import { Solution } from '../../shared/interfaces/solution.interface';
import { SolutionCardComponent } from '../../shared/components/solution-card/solution-card.component';
import { siteConfig } from '../../core/config/site.config';
import { FormsModule } from '@angular/forms';
import { Subject } from 'rxjs';
import { debounceTime, distinctUntilChanged } from 'rxjs/operators';

@Component({
  selector: 'tc-home',
  standalone: true,
  imports: [
    CommonModule, 
    RouterModule, 
    CarouselModule, 
    ProgressSpinnerModule, 
    MessageModule, 
    SolutionCardComponent,
    InputTextModule,
    FormsModule
  ],
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})
export class HomeComponent implements OnInit {
  config = siteConfig;
  recommendedSolutions: Solution[] = [];
  newSolutions: Solution[] = [];
  searchResults: Solution[] = [];
  loading = true;
  loadingNew = true;
  loadingSearch = false;
  error: string | null = null;
  newSolutionsError: string | null = null;
  searchError: string | null = null;
  searchKeyword = '';
  private searchSubject = new Subject<string>();

  responsiveOptions = [
    {
      breakpoint: '1400px',
      numVisible: 3,
      numScroll: 1
    },
    {
      breakpoint: '1024px',
      numVisible: 2,
      numScroll: 1
    },
    {
      breakpoint: '768px',
      numVisible: 1,
      numScroll: 1
    }
  ];

  constructor(private solutionService: SolutionService) {
    this.searchSubject
      .pipe(
        debounceTime(300),
        distinctUntilChanged()
      )
      .subscribe(keyword => {
        if (keyword.trim()) {
          this.performSearch(keyword);
        } else {
          this.searchResults = [];
          this.loadingSearch = false;
        }
      });
  }

  ngOnInit(): void {
    this.loadRecommendedSolutions();
    this.loadNewSolutions();
  }

  private loadRecommendedSolutions(): void {
    this.solutionService.getRecommendedSolutions()
      .subscribe({
        next: (response) => {
          this.recommendedSolutions = response.data;
          this.loading = false;
        },
        error: (error) => {
          this.error = 'Failed to load recommended solutions';
          this.loading = false;
          console.error('Error loading solutions:', error);
        }
      });
  }

  private loadNewSolutions(): void {
    this.loadingNew = true;
    this.solutionService.getNewSolutions()
      .subscribe({
        next: (response) => {
          this.newSolutions = response.data;
          this.loadingNew = false;
        },
        error: (error) => {
          this.newSolutionsError = 'Failed to load new solutions';
          this.loadingNew = false;
          console.error('Error loading new solutions:', error);
        }
      });
  }

  onSearch(event: Event): void {
    const keyword = (event.target as HTMLInputElement).value;
    this.searchKeyword = keyword;
    this.searchSubject.next(keyword);
  }

  private performSearch(keyword: string): void {
    this.loadingSearch = true;
    this.searchError = null;
    this.solutionService.searchSolutions(keyword)
      .subscribe({
        next: (response) => {
          this.searchResults = response.data;
          this.loadingSearch = false;
        },
        error: (error) => {
          this.searchError = 'Failed to search solutions. Please try again.';
          this.loadingSearch = false;
          console.error('Search error:', error);
        }
      });
  }
} 