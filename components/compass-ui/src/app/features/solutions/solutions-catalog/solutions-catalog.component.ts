import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { SolutionService } from '../../../core/services/solution.service';
import { SolutionCardComponent } from '../../../shared/components/solution-card/solution-card.component';
import { Solution } from '../../../shared/interfaces/solution.interface';

// PrimeNG imports
import { PaginatorModule } from 'primeng/paginator';
import { DropdownModule } from 'primeng/dropdown';
import { MultiSelectModule } from 'primeng/multiselect';
import { ProgressSpinnerModule } from 'primeng/progressspinner';
import { MessageModule } from 'primeng/message';

interface SolutionFilters {
  category?: string;
  department?: string;
  team?: string;
  recommend_status?: 'BUY' | 'HOLD' | 'SELL';
  radar_status?: 'ADOPT' | 'TRIAL' | 'ASSESS' | 'HOLD';
  stage?: 'DEVELOPING' | 'UAT' | 'PRODUCTION' | 'DEPRECATED' | 'RETIRED';
  sort: string;
}

interface SolutionParams extends SolutionFilters {
  skip: number;
  limit: number;
  [key: string]: string | number | undefined;
}

@Component({
  selector: 'app-solutions-catalog',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    SolutionCardComponent,
    PaginatorModule,
    DropdownModule,
    MultiSelectModule,
    ProgressSpinnerModule,
    MessageModule
  ],
  templateUrl: './solutions-catalog.component.html',
  styleUrls: ['./solutions-catalog.component.scss']
})
export class SolutionsCatalogComponent implements OnInit {
  solutions: Solution[] = [];
  loading = true;
  error: string | null = null;
  totalRecords = 0;
  
  // Pagination
  currentPage = 0;
  pageSize = 9;

  // Filters
  filters: SolutionFilters = {
    sort: '-created_at'
  };

  // Filter options
  recommendStatusOptions = [
    { label: 'Buy', value: 'BUY' },
    { label: 'Hold', value: 'HOLD' },
    { label: 'Sell', value: 'SELL' }
  ];

  radarStatusOptions = [
    { label: 'Adopt', value: 'ADOPT' },
    { label: 'Trial', value: 'TRIAL' },
    { label: 'Assess', value: 'ASSESS' },
    { label: 'Hold', value: 'HOLD' }
  ];

  stageOptions = [
    { label: 'Developing', value: 'DEVELOPING' },
    { label: 'UAT', value: 'UAT' },
    { label: 'Production', value: 'PRODUCTION' },
    { label: 'Deprecated', value: 'DEPRECATED' },
    { label: 'Retired', value: 'RETIRED' }
  ];

  sortOptions = [
    { label: 'Newest First', value: '-created_at' },
    { label: 'Oldest First', value: 'created_at' },
    { label: 'Name A-Z', value: 'name' },
    { label: 'Name Z-A', value: '-name' }
  ];

  constructor(private solutionService: SolutionService) {
    console.log('SolutionsCatalogComponent constructed');
  }

  ngOnInit(): void {
    console.log('SolutionsCatalogComponent initialized');
    this.loadSolutions();
  }

  onPageChange(event: any): void {
    this.currentPage = event.page;
    this.pageSize = event.rows;
    this.loadSolutions();
  }

  onFilterChange(): void {
    this.currentPage = 0;
    this.loadSolutions();
  }

  private loadSolutions(): void {
    this.loading = true;
    const params: SolutionParams = {
      skip: this.currentPage * this.pageSize,
      limit: this.pageSize,
      ...this.filters
    };

    // Remove any null or undefined values
    Object.keys(params).forEach(key => {
      if (params[key] === null || params[key] === undefined) {
        delete params[key];
      }
    });

    this.solutionService.getSolutions(params).subscribe({
      next: (response) => {
        this.solutions = response.data;
        this.totalRecords = response.total;
        this.loading = false;
      },
      error: (error) => {
        this.error = 'Failed to load solutions';
        this.loading = false;
        console.error('Error loading solutions:', error);
      }
    });
  }
} 