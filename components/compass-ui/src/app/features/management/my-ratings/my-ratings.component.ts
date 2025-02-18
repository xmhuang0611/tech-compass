import { CommonModule, DatePipe } from "@angular/common";
import { Component, OnInit } from "@angular/core";
import { FormsModule } from "@angular/forms";
import { RouterModule } from "@angular/router";
import { ConfirmationService, MessageService } from "primeng/api";
import { finalize } from "rxjs";
import {
    Rating,
    RatingResponse,
    RatingService,
} from "../../../core/services/rating.service";

// PrimeNG Components
import { ButtonModule } from "primeng/button";
import { CheckboxModule } from "primeng/checkbox";
import { ConfirmDialogModule } from "primeng/confirmdialog";
import { DialogModule } from "primeng/dialog";
import { InputTextareaModule } from "primeng/inputtextarea";
import { ProgressSpinnerModule } from "primeng/progressspinner";
import { RatingModule } from "primeng/rating";
import { TableModule } from "primeng/table";
import { ToastModule } from "primeng/toast";

@Component({
  selector: "app-my-ratings",
  templateUrl: "./my-ratings.component.html",
  styleUrls: ["./my-ratings.component.scss"],
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    RouterModule,
    DatePipe,
    ButtonModule,
    CheckboxModule,
    ConfirmDialogModule,
    DialogModule,
    InputTextareaModule,
    ProgressSpinnerModule,
    RatingModule,
    TableModule,
    ToastModule,
  ],
  providers: [ConfirmationService, MessageService],
})
export class MyRatingsComponent implements OnInit {
  ratings: Rating[] = [];
  totalRecords = 0;
  loading = false;
  pageSize = 10;
  rowsPerPageOptions = [10, 20, 50];
  editDialogVisible = false;
  editingRating: Rating = {} as Rating;

  constructor(
    private ratingService: RatingService,
    private messageService: MessageService,
    private confirmationService: ConfirmationService
  ) {}

  ngOnInit() {
    this.loadRatings();
  }

  loadRatings(skip: number = 0) {
    this.loading = true;
    this.ratingService
      .getMyRatings(skip, this.pageSize)
      .pipe(finalize(() => (this.loading = false)))
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
    this.loadRatings(event.first);
  }

  editRating(rating: Rating) {
    this.editingRating = { ...rating };
    this.editDialogVisible = true;
  }

  saveRating() {
    if (!this.editingRating.score) return;

    this.ratingService
      .updateRating(
        this.editingRating._id,
        this.editingRating.score,
        this.editingRating.comment,
        this.editingRating.is_adopted_user
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
        },
        error: (error) => {
          this.messageService.add({
            severity: "error",
            summary: "Error",
            detail: "Failed to update rating",
          });
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

  deleteRating(rating: Rating) {
    this.ratingService.deleteRating(rating._id).subscribe({
      next: (response) => {
        if (response.success) {
          this.messageService.add({
            severity: "success",
            summary: "Success",
            detail: "Rating deleted successfully",
          });
          this.loadRatings();
        }
      },
      error: (error) => {
        this.messageService.add({
          severity: "error",
          summary: "Error",
          detail: "Failed to delete rating",
        });
      },
    });
  }
}
