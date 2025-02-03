import { Component, OnInit, HostListener, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, ActivatedRoute, RouterModule } from '@angular/router';
import { SolutionService } from '../../core/services/solution.service';
import { SolutionCardComponent } from '../../shared/components/solution-card/solution-card.component';
import { Solution } from '../../shared/interfaces/solution.interface';
import { CategoryService, Category } from '../../core/services/category.service';
import { DepartmentService } from '../../core/services/department.service';
import { Subscription } from 'rxjs';

// PrimeNG imports
import { DropdownModule } from 'primeng/dropdown';
import { MultiSelectModule } from 'primeng/multiselect';
import { ProgressSpinnerModule } from 'primeng/progressspinner';
import { MessageModule } from 'primeng/message';
import { TooltipModule } from 'primeng/tooltip';
import { BreadcrumbModule } from 'primeng/breadcrumb';
import { ButtonModule } from 'primeng/button';

interface SolutionFilters {
  category?: string;
  department?: string;
  team?: string;
  recommend_status?: 'ADOPT' | 'TRIAL' | 'ASSESS' | 'HOLD';
  stage?: 'DEVELOPING' | 'UAT' | 'PRODUCTION' | 'DEPRECATED' | 'RETIRED';
  sort: string;
}

interface SolutionParams extends SolutionFilters {
  skip: number;
  limit: number;
  [key: string]: string | number | undefined;
}

interface CategoryOption {
  label: string;
  value: string | null;
  title?: string; // For tooltip
}

interface DropdownOption {
  label: string;
  value: string | null;
}

@Component({
  selector: 'app-solution-catalog',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    SolutionCardComponent,
    DropdownModule,
    MultiSelectModule,
    ProgressSpinnerModule,
    MessageModule,
    TooltipModule,
    BreadcrumbModule,
    ButtonModule,
    RouterModule
  ],
  templateUrl: './solution-catalog.component.html',
  styleUrls: ['./solution-catalog.component.scss'],
  providers: [CategoryService, DepartmentService]
})
export class SolutionCatalogComponent implements OnInit, OnDestroy {
  solutions: Solution[] = [];
  loading = true;
  loadingMore = false;
  error: string | null = null;
  totalRecords = 0;
  
  // Pagination
  currentPage = 0;
  initialPageSize = 15;
  loadMoreSize = 15;
  hasMore = true;

  // Filters
  filters: SolutionFilters = {
    sort: 'name'
  };

  categoryOptions: CategoryOption[] = [
    { label: 'All', value: null }
  ];

  departmentOptions: DropdownOption[] = [
    { label: 'All', value: null }
  ];

  // Filter options
  recommendStatusOptions = [
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

  private queryParamSubscription: Subscription | null = null;

  constructor(
    private solutionService: SolutionService,
    private categoryService: CategoryService,
    private departmentService: DepartmentService,
    private router: Router,
    private route: ActivatedRoute
  ) {}

  ngOnInit(): void {
    this.loadCategories();
    this.loadDepartments();
    
    // Subscribe to URL query parameters
    this.queryParamSubscription = this.route.queryParams.subscribe(params => {
      // Reset filters to default
      this.filters = {
        sort: 'name'
      };

      // Update filters from URL parameters
      if (params['category']) this.filters.category = params['category'];
      if (params['department']) this.filters.department = params['department'];
      if (params['team']) this.filters.team = params['team'];
      if (params['recommend_status']) this.filters.recommend_status = params['recommend_status'] as any;
      if (params['stage']) this.filters.stage = params['stage'] as any;
      if (params['sort']) this.filters.sort = params['sort'];

      // Reset pagination
      this.currentPage = 0;
      this.solutions = [];
      this.hasMore = true;

      // Load solutions with new filters
      this.loadSolutions();
    });
  }

  ngOnDestroy(): void {
    if (this.queryParamSubscription) {
      this.queryParamSubscription.unsubscribe();
    }
  }

  @HostListener('window:scroll', ['$event'])
  onScroll(): void {
    if (this.isNearBottom() && !this.loadingMore && this.hasMore) {
      this.loadMore();
    }
  }

  private isNearBottom(): boolean {
    const threshold = 200;
    const position = window.scrollY + window.innerHeight;
    const height = document.documentElement.scrollHeight;
    return position > height - threshold;
  }

  onFilterChange(): void {
    // Reset pagination
    this.currentPage = 0;
    this.solutions = [];
    this.hasMore = true;

    // Update URL with current filters
    const queryParams: { [key: string]: string } = {};
    Object.entries(this.filters).forEach(([key, value]) => {
      // Only include non-null, non-undefined, non-empty values, and non-default values
      if (value !== null && value !== undefined && value !== '' && 
          !(key === 'sort' && value === 'name')) { // Don't include default sort
        queryParams[key] = value;
      }
    });

    // Update URL without reloading the page
    this.router.navigate([], {
      relativeTo: this.route,
      queryParams,
      // Remove queryParamsHandling: 'merge' to ensure old params are removed
      replaceUrl: true
    });

    // Load solutions immediately instead of waiting for queryParams subscription
    this.loadSolutions();
  }

  private loadMore(): void {
    if (this.loadingMore) return;
    
    this.loadingMore = true;
    this.currentPage++;
    
    const params: SolutionParams = {
      skip: this.currentPage * this.loadMoreSize,
      limit: this.loadMoreSize,
      ...this.filters
    };

    // Remove any null, undefined, or empty string values
    Object.keys(params).forEach(key => {
      if (params[key] === null || params[key] === undefined || params[key] === '') {
        delete params[key];
      }
    });

    this.solutionService.getSolutions(params).subscribe({
      next: (response) => {
        this.solutions = [...this.solutions, ...response.data];
        this.totalRecords = response.total;
        this.hasMore = this.solutions.length < this.totalRecords;
        this.loadingMore = false;
      },
      error: (error) => {
        this.error = 'Failed to load more solutions';
        this.loadingMore = false;
        console.error('Error loading solutions:', error);
      }
    });
  }

  private loadSolutions(): void {
    this.loading = true;
    this.error = null; // Reset error state
    
    const params: SolutionParams = {
      skip: 0,
      limit: this.initialPageSize,
      ...this.filters
    };

    // Remove any null, undefined, or empty string values
    Object.keys(params).forEach(key => {
      if (params[key] === null || params[key] === undefined || params[key] === '') {
        delete params[key];
      }
    });

    this.solutionService.getSolutions(params).subscribe({
      next: (response) => {
        this.solutions = response.data;
        this.totalRecords = response.total;
        this.hasMore = this.solutions.length < this.totalRecords;
        this.loading = false;
      },
      error: (error) => {
        this.error = 'Failed to load solutions';
        this.loading = false;
        console.error('Error loading solutions:', error);
      }
    });
  }

  private loadCategories(): void {
    this.categoryService.getCategories().subscribe({
      next: (response) => {
        const categories = response.data.map(category => ({
          label: `${category.name} (${category.usage_count})`,
          value: category.name,
          title: `${category.name} - Used in ${category.usage_count} solution${category.usage_count !== 1 ? 's' : ''}`
        }));
        this.categoryOptions = [
          { label: 'All', value: null },
          ...categories.sort((a, b) => a.label.localeCompare(b.label))
        ];
      },
      error: (error: Error) => {
        console.error('Error loading categories:', error);
      }
    });
  }

  private loadDepartments(): void {
    this.departmentService.getDepartments().subscribe({
      next: (response) => {
        const departments = response.data.map(dept => ({
          label: dept,
          value: dept
        }));
        this.departmentOptions = [
          { label: 'All', value: null },
          ...departments.sort((a, b) => a.label.localeCompare(b.label))
        ];
      },
      error: (error: Error) => {
        console.error('Error loading departments:', error);
      }
    });
  }

  getSelectedCategoryTooltip(): string {
    if (!this.filters.category) return '';
    const selectedOption = this.categoryOptions.find(opt => opt.value === this.filters.category);
    return selectedOption?.title || '';
  }
}