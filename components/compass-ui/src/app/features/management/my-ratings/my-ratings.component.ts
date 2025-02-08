import { Component, OnInit } from "@angular/core";
import { CommonModule } from "@angular/common";
import { FormsModule } from "@angular/forms";
import { RouterModule } from "@angular/router";
import { MessageService } from "primeng/api";
import {
  RatingService,
  Rating,
  RatingResponse,
} from "../../../core/services/rating.service";
import { finalize } from "rxjs";

// PrimeNG Components
import { ButtonModule } from "primeng/button";
import { TableModule } from "primeng/table";
import { ToastModule } from "primeng/toast";
import { DialogModule } from "primeng/dialog";
import { InputTextareaModule } from "primeng/inputtextarea";
import { ConfirmDialogModule } from "primeng/confirmdialog";
import { ConfirmationService } from "primeng/api";
import { RatingModule } from "primeng/rating";

@Component({
  selector: "app-my-ratings",
  templateUrl: "./my-ratings.component.html",
  styleUrls: ["./my-ratings.component.scss"],
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    RouterModule,
    ButtonModule,
    TableModule,
    ToastModule,
    DialogModule,
    InputTextareaModule,
    ConfirmDialogModule,
    RatingModule,
  ],
  providers: [MessageService, ConfirmationService],
})
export class MyRatingsComponent implements OnInit {
  ratings: Rating[] = [];
  loading = false;
  totalRecords = 0;
  pageSize = 10;
  currentPage = 0;
  rowsPerPageOptions: number[] = [5, 10, 20, 50];

  editDialogVisible = false;
  editingRating: Partial<Rating> = {};

  constructor(
    private ratingService: RatingService,
    private messageService: MessageService,
    private confirmationService: ConfirmationService
  ) {}

  ngOnInit() {
    this.loadRatings();
  }

  loadRatings() {
    this.loading = true;
    const skip = this.currentPage * this.pageSize;

    this.ratingService
      .getMyRatings(skip, this.pageSize)
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
        error: (error) => {
          this.messageService.add({
            severity: "error",
            summary: "Error",
            detail: "Failed to load ratings",
          });
        },
      });
  }

  onPageChange(event: any) {
    this.pageSize = event.rows;
    this.currentPage = Math.floor(event.first / event.rows);
    this.loadRatings();
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
        next: (response: { success: boolean }) => {
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
        error: (error) => {
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
        // 204 response will be null, which is expected for successful deletion
        this.messageService.add({
          severity: "success",
          summary: "Success",
          detail: "Rating deleted successfully",
        });
        this.loadRatings();
      },
      error: (error) => {
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
