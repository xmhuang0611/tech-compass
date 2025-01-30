import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { CarouselModule } from 'primeng/carousel';
import { ProgressSpinnerModule } from 'primeng/progressspinner';
import { MessageModule } from 'primeng/message';
import { SolutionService } from '../../core/services/solution.service';
import { Solution } from '../../shared/interfaces/solution.interface';
import { SolutionCardComponent } from '../../shared/components/solution-card/solution-card.component';
import { siteConfig } from '../../core/config/site.config';

@Component({
  selector: 'tc-home',
  standalone: true,
  imports: [
    CommonModule, 
    RouterModule, 
    CarouselModule, 
    ProgressSpinnerModule, 
    MessageModule, 
    SolutionCardComponent
  ],
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})
export class HomeComponent implements OnInit {
  config = siteConfig;
  recommendedSolutions: Solution[] = [];
  newSolutions: Solution[] = [];
  loading = true;
  loadingNew = true;
  error: string | null = null;
  newSolutionsError: string | null = null;

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

  constructor(private solutionService: SolutionService) {}

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
} 