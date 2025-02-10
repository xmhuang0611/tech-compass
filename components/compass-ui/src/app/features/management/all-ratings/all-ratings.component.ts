import { Component, OnInit, OnDestroy } from "@angular/core";
import { CommonModule } from "@angular/common";
import { FormsModule } from "@angular/forms";
import { RouterModule } from "@angular/router";
import { MessageService } from "primeng/api";
import { RatingService, Rating, RatingResponse } from "../../../core/services/rating.service";
import { Subject, debounceTime, takeUntil, finalize } from "rxjs";

// PrimeNG Components
import { ButtonModule } from "primeng/button";
import { TableModule } from "primeng/table";
import { ToastModule } from "primeng/toast";
import { DialogModule } from "primeng/dialog";
import { ConfirmDialogModule } from "primeng/confirmdialog";
import { ConfirmationService } from "primeng/api";
import { TagModule } from "primeng/tag";
import { InputTextModule } from "primeng/inputtext";
import { DropdownModule } from "primeng/dropdown";
import { RatingModule } from "primeng/rating";
import { InputTextareaModule } from "primeng/inputtextarea";

@Component({
  selector: "app-all-ratings",
  templateUrl: "./all-ratings.component.html",
  styleUrls: ["./all-ratings.component.scss"],
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    RouterModule,
    ButtonModule,
    TableModule,
    ToastModule,
    DialogModule,
    ConfirmDialogModule,
    TagModule,
    InputTextModule,
    DropdownModule,
    RatingModule,
    InputTextareaModule,
  ],
  providers: [MessageService, ConfirmationService],
})
export class AllRatingsComponent implements OnInit, OnDestroy {
  ratings: Rating[] = [];
  loading = false;
  totalRecords = 0;
  pageSize = 10;
  currentPage = 0;
  rowsPerPageOptions: number[] = [5, 10, 20, 50];

  editDialogVisible = false;
  editingRating: Partial<Rating> = {};

  // Filters
  filters = {
    solution_slug: "",
    score: null as number | null,
  };

  scoreOptions = [
    { label: "All Scores", value: null },
    { label: "5 Stars", value: 5 },
    { label: "4 Stars", value: 4 },
    { label: "3 Stars", value: 3 },
    { label: "2 Stars", value: 2 },
    { label: "1 Star", value: 1 },
  ];

  private destroy$ = new Subject<void>();
  private searchSubject = new Subject<void>();

  constructor(
    private ratingService: RatingService,
    private messageService: MessageService,
    private confirmationService: ConfirmationService
  ) {
    // Setup search debounce
    this.searchSubject
      .pipe(debounceTime(300), takeUntil(this.destroy$))
      .subscribe(() => {
        this.resetAndReload();
      });
  }

  ngOnInit() {
    this.loadRatings();
  }

  ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
  }

  onFilterChange() {
    this.searchSubject.next();
  }

  loadRatings() {
    this.loading = true;
    const skip = this.currentPage * this.pageSize;

    const filters = {
      solution_slug: this.filters.solution_slug || undefined,
      score: this.filters.score || undefined,
    };

    this.ratingService
      .getAllRatings(skip, this.pageSize, filters)
      .pipe(
        finalize(() => {
          this.loading = false;
        })
      )
      .subscribe({
        next: (response: RatingResponse) => {
          if (response.success) {
            this.ratings = response.data;
            this.totalRecords = response.total;
          }
        },
        error: (error: any) => {
          this.messageService.add({
            severity: "error",
            summary: "Error",
            detail: "Failed to load ratings",
          });
        },
      });
  }

  private resetAndReload() {
    this.currentPage = 0;
    this.ratings = [];
    this.loadRatings();
  }

  onPageChange(event: any) {
    this.pageSize = event.rows;
    this.currentPage = Math.floor(event.first / event.rows);
    this.loadRatings();
  }

  getRatingSeverity(score: number): "success" | "info" | "warning" | "danger" {
    if (score >= 4) return "success";
    if (score >= 3) return "info";
    if (score >= 2) return "warning";
    return "danger";
  }

  editRating(rating: Rating) {
    this.editingRating = { ...rating };
    this.editDialogVisible = true;
  }

  saveRating() {
    if (!this.editingRating._id || !this.editingRating.score) {
      return;
    }

    this.loading = true;
    this.ratingService
      .updateRating(
        this.editingRating._id,
        this.editingRating.score,
        this.editingRating.comment
      )
      .subscribe({
        next: (response) => {
          if (response.success) {
            this.messageService.add({
              severity: "success",
              summary: "Success",
              detail: "Rating updated successfully",
            });
            this.editDialogVisible = false;
            this.loadRatings();
          }
          this.loading = false;
        },
        error: (error: any) => {
          this.messageService.add({
            severity: "error",
            summary: "Error",
            detail: error.error?.detail || "Failed to update rating",
          });
          this.loading = false;
        },
      });
  }

  confirmDelete(rating: Rating) {
    this.confirmationService.confirm({
      message: "Are you sure you want to delete this rating?",
      accept: () => {
        this.deleteRating(rating);
      },
    });
  }

  private deleteRating(rating: Rating) {
    this.loading = true;

    this.ratingService.deleteRating(rating._id).subscribe({
      next: (response) => {
        this.messageService.add({
          severity: "success",
          summary: "Success",
          detail: "Rating deleted successfully",
        });
        this.loadRatings();
      },
      error: (error: any) => {
        this.messageService.add({
          severity: "error",
          summary: "Error",
          detail: error.error?.detail || "Failed to delete rating",
        });
        this.loading = false;
      },
    });
  }
} 