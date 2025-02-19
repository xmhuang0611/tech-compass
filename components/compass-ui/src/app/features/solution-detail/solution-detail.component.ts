import { CommonModule, DatePipe } from "@angular/common";
import { HttpClient } from "@angular/common/http";
import { Component, OnDestroy, OnInit } from "@angular/core";
import { FormsModule } from "@angular/forms";
import { ActivatedRoute, Router, RouterModule } from "@angular/router";
import { MessageService } from "primeng/api";
import { DialogService } from "primeng/dynamicdialog";
import { BehaviorSubject, Subject, finalize, takeUntil } from "rxjs";
import { environment } from "../../../environments/environment";
import { LoginDialogComponent } from "../../core/components/login-dialog/login-dialog.component";
import { AuthService } from "../../core/services/auth.service";
import { Comment, CommentService } from "../../core/services/comment.service";
import type { Rating } from "../../core/services/rating.service";
import { RatingService } from "../../core/services/rating.service";
import { AdoptedUser, SolutionService } from "../../core/services/solution.service";
import { Solution } from "../../shared/interfaces/solution.interface";

// PrimeNG Components
import { BreadcrumbModule } from "primeng/breadcrumb";
import { ButtonModule } from "primeng/button";
import { CardModule } from "primeng/card";
import { CheckboxModule } from "primeng/checkbox";
import { ChipModule } from "primeng/chip";
import { InputTextareaModule } from "primeng/inputtextarea";
import { ProgressSpinnerModule } from "primeng/progressspinner";
import { RatingModule } from "primeng/rating";
import { TabViewModule } from "primeng/tabview";
import { TagModule } from "primeng/tag";
import { ToastModule } from "primeng/toast";
import { TooltipModule } from "primeng/tooltip";

// Markdown
import { MarkdownModule } from "ngx-markdown";

type Severity =
  | "success"
  | "info"
  | "warning"
  | "danger"
  | "secondary"
  | "contrast";

@Component({
  selector: "app-solution-detail",
  templateUrl: "./solution-detail.component.html",
  styleUrls: ["./solution-detail.component.scss"],
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    RouterModule,
    DatePipe,
    BreadcrumbModule,
    ButtonModule,
    CardModule,
    CheckboxModule,
    ChipModule,
    InputTextareaModule,
    ProgressSpinnerModule,
    RatingModule,
    TabViewModule,
    TagModule,
    ToastModule,
    TooltipModule,
    MarkdownModule,
  ],
  providers: [DialogService],
})
export class SolutionDetailComponent implements OnInit, OnDestroy {
  private destroy$ = new Subject<void>();
  private userCommentsPage = 0;
  private ratingsPage = 0;

  solution$ = new BehaviorSubject<Solution | null>(null);
  officialComments$ = new BehaviorSubject<Comment[]>([]);
  userComments$ = new BehaviorSubject<Comment[]>([]);
  ratings$ = new BehaviorSubject<Rating[]>([]);

  loading = true;
  loadingOfficialComments = false;
  loadingUserComments = false;
  loadingRatings = false;
  hasMoreUserComments = true;
  hasMoreRatings = true;
  totalOfficialComments = 0;
  totalUserComments = 0;
  totalRatings = 0;
  activeTab = 0;
  newComment = "";
  newCommentIsAdopted = false;
  newRating = {
    score: 0,
    comment: "",
    is_adopted_user: false
  };
  isLoggedIn = false;

  adoptedUsers$ = new BehaviorSubject<AdoptedUser[]>([]);
  loadingAdoptedUsers = false;
  totalAdoptedUsers = 0;
  adoptedUsersPage = 0;
  hasMoreAdoptedUsers = true;

  environment = environment;

  constructor(
    private route: ActivatedRoute,
    private http: HttpClient,
    private messageService: MessageService,
    private authService: AuthService,
    private dialogService: DialogService,
    private commentService: CommentService,
    private ratingService: RatingService,
    private solutionService: SolutionService,
    private router: Router
  ) {}

  ngOnInit() {
    this.route.params.pipe(takeUntil(this.destroy$)).subscribe((params) => {
      const slug = params["slug"];
      this.loadSolution(slug);
      this.loadComments(slug);
      this.loadRatings(slug);
      this.loadAdoptedUsers(slug);
    });

    this.authService.currentUser$.subscribe((user) => {
      this.isLoggedIn = !!user;
    });
  }

  ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
  }

  getStageSeverity(stage: string): Severity {
    const severityMap: { [key: string]: Severity } = {
      DEVELOPING: "warning",
      UAT: "info",
      PRODUCTION: "success",
      DEPRECATED: "danger",
      RETIRED: "danger",
    };
    return severityMap[stage] || "info";
  }

  getRecommendStatusSeverity(status: string): Severity {
    const severityMap: { [key: string]: Severity } = {
      ADOPT: "success",
      TRIAL: "info",
      ASSESS: "warning",
      HOLD: "danger",
    };
    return severityMap[status] || "info";
  }

  getAdoptionLevelSeverity(level: string): Severity {
    const severityMap: { [key: string]: Severity } = {
      PILOT: "warning",
      TEAM: "info",
      DEPARTMENT: "success",
      ENTERPRISE: "success",
      INDUSTRY: "success",
    };
    return severityMap[level] || "info";
  }

  private loadSolution(slug: string) {
    this.loading = true;
    this.http
      .get<any>(`${environment.apiUrl}/solutions/${slug}`)
      .pipe(finalize(() => (this.loading = false)))
      .subscribe({
        next: (response) => {
          if (response.success) {
            this.solution$.next(response.data);
          }
        },
        error: (error) => {
          this.messageService.add({
            severity: "error",
            summary: "Error",
            detail: "Failed to load solution details",
          });
        },
      });
  }

  loadComments(slug: string, loadMore = false) {
    if (!loadMore) {
      this.userCommentsPage = 0;
      this.officialComments$.next([]);
      this.userComments$.next([]);
    }

    // Load OFFICIAL comments (max 10)
    this.loadingOfficialComments = true;
    this.commentService
      .getSolutionComments(slug, 0, 10, "OFFICIAL")
      .pipe(
        finalize(() => {
          this.loadingOfficialComments = false;
        }),
        takeUntil(this.destroy$)
      )
      .subscribe({
        next: (response) => {
          if (response.success) {
            this.officialComments$.next(response.data);
            this.totalOfficialComments = response.total;
          }
        },
        error: (error) => {
          this.messageService.add({
            severity: "error",
            summary: "Error",
            detail: "Failed to load official comments",
          });
        },
      });

    // Load USER comments
    if (!loadMore) {
      this.userCommentsPage = 0;
      this.userComments$.next([]);
    }

    this.loadingUserComments = true;
    this.commentService
      .getSolutionComments(slug, this.userCommentsPage * 10, 10, "USER")
      .pipe(
        finalize(() => {
          this.loadingUserComments = false;
        }),
        takeUntil(this.destroy$)
      )
      .subscribe({
        next: (response) => {
          if (response.success) {
            const currentComments = this.userComments$.value;
            this.userComments$.next([...currentComments, ...response.data]);
            this.totalUserComments = response.total;
            this.hasMoreUserComments = currentComments.length + response.data.length < response.total;
            this.userCommentsPage++;
          }
        },
        error: (error) => {
          this.messageService.add({
            severity: "error",
            summary: "Error",
            detail: "Failed to load user comments",
          });
        },
      });
  }

  loadRatings(slug: string, loadMore = false) {
    if (!loadMore) {
      this.ratingsPage = 0;
      this.ratings$.next([]);
      this.hasMoreRatings = true;
    }

    if (!this.hasMoreRatings || this.loadingRatings) {
      return;
    }

    this.loadingRatings = true;
    const skip = this.ratingsPage * 10;

    this.ratingService
      .getSolutionRatings(slug, skip, 10)
      .pipe(finalize(() => (this.loadingRatings = false)))
      .subscribe({
        next: (response) => {
          if (response.success) {
            const currentRatings = this.ratings$.value;
            this.ratings$.next([...currentRatings, ...response.data]);
            this.totalRatings = response.total;
            this.hasMoreRatings =
              currentRatings.length + response.data.length < response.total;
            this.ratingsPage++;
          }
        },
        error: (error) => {
          this.messageService.add({
            severity: "error",
            summary: "Error",
            detail: "Failed to load ratings",
          });
        },
      });
  }

  submitComment(slug: string) {
    if (!this.newComment.trim()) return;

    this.commentService
      .addComment(slug, {
        content: this.newComment,
        is_adopted_user: this.newCommentIsAdopted
      })
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (response) => {
          if (response.success) {
            this.messageService.add({
              severity: "success",
              summary: "Success",
              detail: "Comment added successfully",
            });
            this.newComment = "";
            this.newCommentIsAdopted = false;
            this.loadComments(slug);
          }
        },
        error: (error) => {
          this.messageService.add({
            severity: "error",
            summary: "Error",
            detail: "Failed to add comment",
          });
        },
      });
  }

  submitRating(slug: string) {
    if (this.newRating.score === 0) return;

    this.ratingService
      .addRating(
        slug,
        this.newRating.score,
        this.newRating.comment,
        this.newRating.is_adopted_user
      )
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (response) => {
          if (response.success) {
            this.messageService.add({
              severity: "success",
              summary: "Success",
              detail: "Rating submitted successfully",
            });
            this.newRating = { score: 0, comment: "", is_adopted_user: false };
            this.loadRatings(slug);
            this.loadSolution(slug);
          }
        },
        error: (error) => {
          this.messageService.add({
            severity: "error",
            summary: "Error",
            detail: "Failed to submit rating",
          });
        },
      });
  }

  showLoginDialog() {
    this.dialogService.open(LoginDialogComponent, {
      header: "Login Required",
      width: "400px",
    });
  }

  canEditSolution(): boolean {
    let canEdit = false;
    this.authService.currentUser$.subscribe(currentUser => {
      const solution = this.solution$.value;

      if (currentUser && solution) {
        // Check if current user is the solution maintainer or a superuser
        canEdit = currentUser.username === solution.maintainer_id || 
                  currentUser.is_superuser;
      }
    });
    return canEdit;
  }

  navigateToEditSolution() {
    this.authService.currentUser$.subscribe(currentUser => {
      const solution = this.solution$.value;
      if (!solution || !currentUser) return;

      const slug = solution.slug;
      if (currentUser.is_superuser) {
        this.router.navigate(['/manage/all-solutions/edit/', slug]);
      } else if (currentUser.username === solution.maintainer_id) {
        this.router.navigate(['/manage/my-solutions/edit/', slug]);
      }
    });
  }

  loadAdoptedUsers(slug: string, loadMore = false) {
    if (!loadMore) {
      this.adoptedUsersPage = 0;
      this.adoptedUsers$.next([]);
      this.hasMoreAdoptedUsers = true;
    }

    if (!this.hasMoreAdoptedUsers || this.loadingAdoptedUsers) {
      return;
    }

    this.loadingAdoptedUsers = true;
    const skip = this.adoptedUsersPage * 10;

    this.solutionService
      .getAdoptedUsers(slug, skip, 10)
      .pipe(finalize(() => (this.loadingAdoptedUsers = false)))
      .subscribe({
        next: (response) => {
          if (response.success) {
            const currentUsers = this.adoptedUsers$.value;
            this.adoptedUsers$.next([...currentUsers, ...response.data]);
            this.totalAdoptedUsers = response.total;
            this.hasMoreAdoptedUsers =
              currentUsers.length + response.data.length < response.total;
            this.adoptedUsersPage++;
          }
        },
        error: (error) => {
          this.messageService.add({
            severity: "error",
            summary: "Error",
            detail: "Failed to load adopted users",
          });
        },
      });
  }

  sendEmail(email: string) {
    const solution = this.solution$.value;
    if (!solution) return;
    
    const subject = encodeURIComponent(`Reach out for tech solution: ${solution.name}`);
    window.location.href = `mailto:${email}?subject=${subject}`;
  }
}
