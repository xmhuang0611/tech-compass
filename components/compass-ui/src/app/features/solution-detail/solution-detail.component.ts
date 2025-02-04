import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule, DatePipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule, ActivatedRoute } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Subject, finalize, takeUntil } from 'rxjs';
import { MessageService } from 'primeng/api';
import { environment } from '../../../environments/environment';
import { AuthService } from '../../core/services/auth.service';
import { DialogService } from 'primeng/dynamicdialog';
import { LoginDialogComponent } from '../../core/components/login-dialog/login-dialog.component';
import { Solution } from '../../shared/interfaces/solution.interface';

// PrimeNG Components
import { BreadcrumbModule } from 'primeng/breadcrumb';
import { ButtonModule } from 'primeng/button';
import { CardModule } from 'primeng/card';
import { ChipModule } from 'primeng/chip';
import { InputTextareaModule } from 'primeng/inputtextarea';
import { ProgressSpinnerModule } from 'primeng/progressspinner';
import { RatingModule } from 'primeng/rating';
import { TabViewModule } from 'primeng/tabview';
import { TagModule } from 'primeng/tag';
import { ToastModule } from 'primeng/toast';

// Markdown
import { MarkdownModule } from 'ngx-markdown';

type Severity = 'success' | 'info' | 'warning' | 'danger' | 'secondary' | 'contrast';

interface Comment {
  _id: string;
  content: string;
  username: string;
  full_name: string;
  created_at: string;
}

interface Rating {
  _id: string;
  score: number;
  comment?: string;
  username: string;
  full_name: string;
  created_at: string;
}

@Component({
  selector: 'app-solution-detail',
  templateUrl: './solution-detail.component.html',
  styleUrls: ['./solution-detail.component.scss'],
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    RouterModule,
    DatePipe,
    BreadcrumbModule,
    ButtonModule,
    CardModule,
    ChipModule,
    InputTextareaModule,
    ProgressSpinnerModule,
    RatingModule,
    TabViewModule,
    TagModule,
    ToastModule,
    MarkdownModule
  ],
  providers: [DialogService]
})
export class SolutionDetailComponent implements OnInit, OnDestroy {
  private destroy$ = new Subject<void>();
  private commentsPage = 1;
  private ratingsPage = 1;
  
  solution$ = new BehaviorSubject<Solution | null>(null);
  comments$ = new BehaviorSubject<Comment[]>([]);
  ratings$ = new BehaviorSubject<Rating[]>([]);
  
  loading = true;
  loadingComments = false;
  loadingRatings = false;
  hasMoreComments = true;
  hasMoreRatings = true;
  totalComments = 0;
  totalRatings = 0;
  activeTab = 0;
  newComment = '';
  newRating = {
    score: 0,
    comment: ''
  };
  isLoggedIn = false;

  constructor(
    private route: ActivatedRoute,
    private http: HttpClient,
    private messageService: MessageService,
    private authService: AuthService,
    private dialogService: DialogService
  ) {
    console.log('SolutionDetailComponent constructed');
  }

  ngOnInit() {
    console.log('SolutionDetailComponent initialized');
    this.route.params.pipe(
      takeUntil(this.destroy$)
    ).subscribe(params => {
      const slug = params['slug'];
      console.log('Loading solution with slug:', slug);
      this.loadSolution(slug);
      this.loadComments(slug);
      this.loadRatings(slug);
    });

    this.authService.currentUser$.subscribe(user => {
      this.isLoggedIn = !!user;
    });
  }

  ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
  }

  getStageSeverity(stage: string): Severity {
    const severityMap: { [key: string]: Severity } = {
      'DEVELOPING': 'warning',
      'UAT': 'info',
      'PRODUCTION': 'success',
      'DEPRECATED': 'danger',
      'RETIRED': 'danger'
    };
    return severityMap[stage] || 'info';
  }

  getRecommendStatusSeverity(status: string): Severity {
    const severityMap: { [key: string]: Severity } = {
      'ADOPT': 'success',
      'TRIAL': 'info',
      'ASSESS': 'warning',
      'HOLD': 'danger'
    };
    return severityMap[status] || 'info';
  }

  private loadSolution(slug: string) {
    console.log('Starting to load solution data');
    this.loading = true;
    this.http.get<any>(`${environment.apiUrl}/solutions/${slug}`).pipe(
      finalize(() => {
        this.loading = false;
        console.log('Finished loading solution data');
      })
    ).subscribe({
      next: (response) => {
        console.log('Solution data received:', response);
        if (response.success) {
          this.solution$.next(response.data);
        }
      },
      error: (error) => {
        console.error('Failed to load solution:', error);
        this.messageService.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to load solution details'
        });
      }
    });
  }

  loadComments(slug: string, loadMore = false) {
    if (!loadMore) {
      this.commentsPage = 1;
      this.comments$.next([]);
      this.hasMoreComments = true;
    }
    
    if (!this.hasMoreComments || this.loadingComments) {
      return;
    }

    console.log('Loading comments for slug:', slug, 'page:', this.commentsPage);
    this.loadingComments = true;
    
    this.http.get<any>(`${environment.apiUrl}/comments/solution/${slug}?page=${this.commentsPage}&page_size=10`).pipe(
      finalize(() => {
        this.loadingComments = false;
        console.log('Finished loading comments');
      })
    ).subscribe({
      next: (response) => {
        console.log('Comments data received:', response);
        if (response.success) {
          const currentComments = this.comments$.value;
          this.comments$.next([...currentComments, ...response.data]);
          this.totalComments = response.total;
          this.hasMoreComments = currentComments.length + response.data.length < response.total;
          this.commentsPage++;
        }
      },
      error: (error) => {
        console.error('Failed to load comments:', error);
        this.messageService.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to load comments'
        });
      }
    });
  }

  loadRatings(slug: string, loadMore = false) {
    if (!loadMore) {
      this.ratingsPage = 1;
      this.ratings$.next([]);
      this.hasMoreRatings = true;
    }
    
    if (!this.hasMoreRatings || this.loadingRatings) {
      return;
    }

    console.log('Loading ratings for slug:', slug, 'page:', this.ratingsPage);
    this.loadingRatings = true;
    
    this.http.get<any>(`${environment.apiUrl}/ratings/solution/${slug}?page=${this.ratingsPage}&page_size=10`).pipe(
      finalize(() => {
        this.loadingRatings = false;
        console.log('Finished loading ratings');
      })
    ).subscribe({
      next: (response) => {
        console.log('Ratings data received:', response);
        if (response.success) {
          const currentRatings = this.ratings$.value;
          this.ratings$.next([...currentRatings, ...response.data]);
          this.totalRatings = response.total;
          this.hasMoreRatings = currentRatings.length + response.data.length < response.total;
          this.ratingsPage++;
        }
      },
      error: (error) => {
        console.error('Failed to load ratings:', error);
        this.messageService.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to load ratings'
        });
      }
    });
  }

  submitComment(slug: string) {
    if (!this.isLoggedIn) {
      this.messageService.add({
        severity: 'warn',
        summary: 'Warning',
        detail: 'Please login to add a comment'
      });
      return;
    }

    if (!this.newComment.trim()) {
      return;
    }

    console.log('Submitting comment for slug:', slug);
    this.http.post<any>(`${environment.apiUrl}/comments/solution/${slug}`, {
      content: this.newComment
    }).subscribe({
      next: (response) => {
        console.log('Comment submission response:', response);
        if (response.success) {
          this.messageService.add({
            severity: 'success',
            summary: 'Success',
            detail: 'Comment added successfully'
          });
          this.newComment = '';
          this.loadComments(slug);
        }
      },
      error: (error) => {
        console.error('Failed to submit comment:', error);
        this.messageService.add({
          severity: 'error',
          summary: 'Error',
          detail: error.error?.detail || 'Failed to add comment'
        });
      }
    });
  }

  submitRating(slug: string) {
    if (!this.isLoggedIn) {
      this.messageService.add({
        severity: 'warn',
        summary: 'Warning',
        detail: 'Please login to submit a rating'
      });
      return;
    }

    if (this.newRating.score === 0) {
      this.messageService.add({
        severity: 'warn',
        summary: 'Warning',
        detail: 'Please select a rating score'
      });
      return;
    }

    console.log('Submitting rating for slug:', slug);
    this.http.post<any>(`${environment.apiUrl}/ratings/solution/${slug}`, this.newRating).subscribe({
      next: (response) => {
        console.log('Rating submission response:', response);
        if (response.success) {
          this.messageService.add({
            severity: 'success',
            summary: 'Success',
            detail: 'Rating submitted successfully'
          });
          this.newRating = { score: 0, comment: '' };
          this.loadRatings(slug);
          this.loadSolution(slug); // Reload solution to update overall rating
        }
      },
      error: (error) => {
        console.error('Failed to submit rating:', error);
        this.messageService.add({
          severity: 'error',
          summary: 'Error',
          detail: error.error?.detail || 'Failed to submit rating'
        });
      }
    });
  }

  showLoginDialog(): void {
    const ref = this.dialogService.open(LoginDialogComponent, {
      header: 'Login',
      width: '400px'
    });

    ref.onClose.subscribe((success: boolean) => {
      if (success) {
        this.messageService.add({
          severity: 'success',
          summary: 'Success',
          detail: 'Logged in successfully'
        });
      }
    });
  }
}
