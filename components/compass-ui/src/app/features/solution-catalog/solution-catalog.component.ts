import { Component, OnInit, HostListener, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, ActivatedRoute, RouterModule } from '@angular/router';
import { SolutionService } from '../../core/services/solution.service';
import { SolutionCardComponent } from '../../shared/components/solution-card/solution-card.component';
import { Solution } from '../../shared/interfaces/solution.interface';
import { CategoryService, Category } from '../../core/services/category.service';
import { DepartmentService } from '../../core/services/department.service';
import { Subscription, Subject } from 'rxjs';
import { debounceTime, distinctUntilChanged } from 'rxjs/operators';
import { TagService, Tag } from '../../core/services/tag.service';
import { ChipModule } from 'primeng/chip';

// PrimeNG imports
import { DropdownModule } from 'primeng/dropdown';
import { MultiSelectModule } from 'primeng/multiselect';
import { ProgressSpinnerModule } from 'primeng/progressspinner';
import { MessageModule } from 'primeng/message';
import { TooltipModule } from 'primeng/tooltip';
import { BreadcrumbModule } from 'primeng/breadcrumb';
import { ButtonModule } from 'primeng/button';
import { InputTextModule } from 'primeng/inputtext';

interface SolutionFilters {
  category?: string;
  department?: string;
  team?: string;
  recommend_status?: 'ADOPT' | 'TRIAL' | 'ASSESS' | 'HOLD';
  sort: string;
  tags?: string;
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
    RouterModule,
    InputTextModule,
    ChipModule
  ],
  templateUrl: './solution-catalog.component.html',
  styleUrls: ['./solution-catalog.component.scss'],
  providers: [CategoryService, DepartmentService, TagService]
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

  sortOptions = [
    { label: 'Newest First', value: '-created_at' },
    { label: 'Oldest First', value: 'created_at' },
    { label: 'Name A-Z', value: 'name' },
    { label: 'Name Z-A', value: '-name' }
  ];

  private queryParamSubscription: Subscription | null = null;

  searchKeyword = '';
  private searchSubject = new Subject<string>();
  private searchSubscription: Subscription | null = null;

  tags: Tag[] = [];
  selectedTags: string[] = [];
  loadingTags = true;
  tagsError: string | null = null;

  constructor(
    private solutionService: SolutionService,
    private categoryService: CategoryService,
    private departmentService: DepartmentService,
    private tagService: TagService,
    private router: Router,
    private route: ActivatedRoute
  ) {
    this.searchSubscription = this.searchSubject
      .pipe(
        debounceTime(300),
        distinctUntilChanged()
      )
      .subscribe(keyword => {
        if (keyword.trim()) {
          this.performSearch(keyword);
        } else {
          this.resetAndLoadSolutions();
        }
      });
  }

  ngOnInit(): void {
    this.loadCategories();
    this.loadDepartments();
    this.loadTags();
    
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
      if (params['sort']) this.filters.sort = params['sort'];
      
      // Handle tags
      this.selectedTags = params['tags'] ? params['tags'].split(',') : [];
      if (this.selectedTags.length > 0) {
        this.filters.tags = params['tags'];
      }

      // Handle search keyword from URL
      this.searchKeyword = params['keyword'] || '';
      
      // Only perform search if there's a keyword, otherwise load solutions once
      if (this.searchKeyword) {
        this.performSearch(this.searchKeyword);
      } else {
        // Reset pagination
        this.currentPage = 0;
        this.solutions = [];
        this.hasMore = true;
        // Load solutions with new filters
        this.loadSolutions();
      }
    });
  }

  ngOnDestroy(): void {
    if (this.queryParamSubscription) {
      this.queryParamSubscription.unsubscribe();
    }
    if (this.searchSubscription) {
      this.searchSubscription.unsubscribe();
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

  onSearch(event: Event): void {
    const keyword = (event.target as HTMLInputElement).value;
    this.searchKeyword = keyword;
    this.searchSubject.next(keyword);
  }

  private performSearch(keyword: string): void {
    this.loading = true;
    this.error = null;
    // Clear filters and selected tags
    this.clearFilters();
    this.selectedTags = [];
    
    // Update URL with only the search keyword
    this.router.navigate([], {
      relativeTo: this.route,
      queryParams: { keyword },
      replaceUrl: true
    });
    
    this.solutionService.searchSolutions(keyword)
      .subscribe({
        next: (response) => {
          this.solutions = response.data;
          this.totalRecords = response.total || 0;
          this.loading = false;
          this.hasMore = false;
        },
        error: () => {
          this.error = 'Failed to search solutions. Please try again.';
          this.loading = false;
        }
      });
  }

  private clearFilters(): void {
    this.filters = {
      sort: 'name'
    };
    this.selectedTags = [];
  }

  onFilterChange(): void {
    this.searchKeyword = '';
    this.currentPage = 0;
    this.solutions = [];
    this.loadSolutions();
    this.updateQueryParams();
  }

  private resetAndLoadSolutions(): void {
    this.currentPage = 0;
    this.solutions = [];
    this.searchKeyword = '';
    this.selectedTags = [];
    this.filters = {
      sort: 'name'
    };
    this.loadSolutions();
    
    // Clear all query parameters
    this.router.navigate([], {
      relativeTo: this.route,
      queryParams: {},
      replaceUrl: true
    });
  }

  private loadMore(): void {
    if (this.loadingMore || this.loading) return;
    
    // Calculate the next skip value
    const nextSkip = this.currentPage * this.loadMoreSize;
    
    // Check if we've already loaded all records
    if (nextSkip >= this.totalRecords) {
      this.hasMore = false;
      return;
    }
    
    this.loadingMore = true;
    
    // Calculate the actual limit for this request
    const remainingRecords = this.totalRecords - nextSkip;
    const actualLimit = Math.min(this.loadMoreSize, remainingRecords);
    
    const params: SolutionParams = {
      skip: nextSkip,
      limit: actualLimit,
      ...this.filters
    };

    // Remove any null, undefined, or empty string values
    Object.keys(params).forEach(key => {
      if (params[key] === null || params[key] === undefined || params[key] === '') {
        delete params[key];
      }
    });

    // Ensure tags are included in the request if selected
    if (this.selectedTags.length > 0) {
      params.tags = this.selectedTags.join(',');
    }

    this.solutionService.getSolutions(params).subscribe({
      next: (response) => {
        this.solutions = [...this.solutions, ...response.data];
        this.totalRecords = response.total;
        // Update hasMore based on next skip value
        this.hasMore = (nextSkip + response.data.length) < this.totalRecords;
        this.loadingMore = false;
        this.currentPage++;
      },
      error: () => {
        this.error = 'Failed to load more solutions. Please try again.';
        this.loadingMore = false;
      }
    });
  }

  private loadSolutions(): void {
    this.loading = true;
    this.error = null;
    
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

    // Ensure tags are included in the request if selected
    if (this.selectedTags.length > 0) {
      params.tags = this.selectedTags.join(',');
    }

    this.solutionService.getSolutions(params).subscribe({
      next: (response) => {
        this.solutions = response.data;
        this.totalRecords = response.total;
        this.hasMore = this.solutions.length < this.totalRecords;
        this.loading = false;
        // Set currentPage to 1 since we've loaded the first page
        this.currentPage = 1;
      },
      error: () => {
        this.error = 'Failed to load solutions. Please try again.';
        this.loading = false;
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
      error: () => {
        this.error = 'Failed to load categories. Please refresh the page to try again.';
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
      error: () => {
        this.error = 'Failed to load departments. Please refresh the page to try again.';
      }
    });
  }

  private loadTags(): void {
    this.loadingTags = true;
    this.tagsError = null;

    this.tagService.getTags().subscribe({
      next: (response) => {
        this.tags = response.data.sort((a, b) => b.usage_count - a.usage_count);
        this.loadingTags = false;
      },
      error: () => {
        this.tagsError = 'Failed to load tags. Please refresh the page to try again.';
        this.loadingTags = false;
      }
    });
  }

  getSelectedCategoryTooltip(): string {
    if (!this.filters.category) return '';
    const selectedOption = this.categoryOptions.find(opt => opt.value === this.filters.category);
    return selectedOption?.title || '';
  }

  private updateQueryParams(): void {
    // Update URL with current filters
    const queryParams: { [key: string]: string } = {};
    
    // Only add non-default values to URL
    Object.entries(this.filters).forEach(([key, value]) => {
      if (value !== null && value !== undefined && value !== '' && 
          !(key === 'sort' && value === 'name')) {
        queryParams[key] = value;
      }
    });

    // Add search keyword if exists
    if (this.searchKeyword) {
      queryParams['keyword'] = this.searchKeyword;
    }

    // Update URL without reloading the page
    this.router.navigate([], {
      relativeTo: this.route,
      queryParams,
      replaceUrl: true
    });
  }

  onTagClick(tag: Tag): void {
    // Clear search keyword
    this.searchKeyword = '';

    const index = this.selectedTags.indexOf(tag.name);
    if (index === -1) {
      this.selectedTags.push(tag.name);
    } else {
      this.selectedTags.splice(index, 1);
    }
    
    if (this.selectedTags.length > 0) {
      this.filters.tags = this.selectedTags.join(',');
    } else {
      delete this.filters.tags;
    }

    this.currentPage = 0;
    this.solutions = [];
    this.loadSolutions();
    this.updateQueryParams();
  }

  isTagSelected(tag: Tag): boolean {
    return this.selectedTags.includes(tag.name);
  }
}