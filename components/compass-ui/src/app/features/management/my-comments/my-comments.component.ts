import { Component, OnInit } from "@angular/core";
import { CommonModule } from "@angular/common";
import { FormsModule } from "@angular/forms";
import { RouterModule } from "@angular/router";
import { MessageService } from "primeng/api";
import {
  CommentService,
  Comment,
} from "../../../core/services/comment.service";
import { BehaviorSubject, finalize } from "rxjs";

// PrimeNG Components
import { ButtonModule } from "primeng/button";
import { TableModule } from "primeng/table";
import { ToastModule } from "primeng/toast";
import { DialogModule } from "primeng/dialog";
import { InputTextareaModule } from "primeng/inputtextarea";
import { ConfirmDialogModule } from "primeng/confirmdialog";
import { ConfirmationService } from "primeng/api";

@Component({
  selector: "app-my-comments",
  templateUrl: "./my-comments.component.html",
  styleUrls: ["./my-comments.component.scss"],
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
  ],
  providers: [MessageService, ConfirmationService],
})
export class MyCommentsComponent implements OnInit {
  comments$ = new BehaviorSubject<Comment[]>([]);
  loading = false;
  totalRecords = 0;
  pageSize = 10;
  currentPage = 1;

  editDialogVisible = false;
  editingComment: Partial<Comment> = {};

  constructor(
    private commentService: CommentService,
    private messageService: MessageService,
    private confirmationService: ConfirmationService
  ) {}

  ngOnInit() {
    this.loadComments();
  }

  loadComments(resetPage = false) {
    if (resetPage) {
      this.currentPage = 1;
    }

    this.loading = true;
    this.commentService
      .getMyComments(this.currentPage, this.pageSize)
      .pipe(finalize(() => (this.loading = false)))
      .subscribe({
        next: (response) => {
          if (response.success) {
            this.comments$.next(response.data);
            this.totalRecords = response.total;

            // If current page is empty (except first page) after deletion, go to previous page
            if (response.data.length === 0 && this.currentPage > 1) {
              this.currentPage--;
              this.loadComments();
            }
          }
        },
        error: (error) => {
          this.messageService.add({
            severity: "error",
            summary: "Error",
            detail: "Failed to load comments",
          });
        },
      });
  }

  onPageChange(event: any) {
    this.currentPage = event.first / event.rows + 1;
    this.pageSize = event.rows;
    this.loadComments();
  }

  editComment(comment: Comment) {
    this.editingComment = { ...comment };
    this.editDialogVisible = true;
  }

  saveComment() {
    if (!this.editingComment._id || !this.editingComment.content?.trim()) {
      return;
    }

    this.commentService
      .updateComment(this.editingComment._id, this.editingComment.content)
      .subscribe({
        next: (response) => {
          if (response.success) {
            this.messageService.add({
              severity: "success",
              summary: "Success",
              detail: "Comment updated successfully",
            });
            this.editDialogVisible = false;
            this.loadComments();
          }
        },
        error: (error) => {
          this.messageService.add({
            severity: "error",
            summary: "Error",
            detail: error.error?.detail || "Failed to update comment",
          });
        },
      });
  }

  confirmDelete(comment: Comment) {
    this.confirmationService.confirm({
      message: "Are you sure you want to delete this comment?",
      accept: () => {
        this.deleteComment(comment);
      },
    });
  }

  deleteComment(comment: Comment) {
    this.commentService.deleteComment(comment._id).subscribe({
      next: (response) => {
        if (response.success) {
          this.messageService.add({
            severity: "success",
            summary: "Success",
            detail: "Comment deleted successfully",
          });

          // Check if this is the last item on the current page
          const currentComments = this.comments$.value;
          const isLastItemOnPage = currentComments.length === 1;
          const isLastPage =
            Math.ceil(this.totalRecords / this.pageSize) === this.currentPage;

          if (isLastItemOnPage && isLastPage && this.currentPage > 1) {
            // If it's the last item on the last page, go to previous page
            this.currentPage--;
          }

          // Update current page data immediately
          const updatedComments = currentComments.filter(
            (c) => c._id !== comment._id
          );
          this.comments$.next(updatedComments);
          this.totalRecords--;

          // Reload data if current page is empty
          if (updatedComments.length === 0 && this.currentPage > 1) {
            this.currentPage--;
            this.loadComments();
          }
        }
      },
      error: (error) => {
        this.messageService.add({
          severity: "error",
          summary: "Error",
          detail: error.error?.detail || "Failed to delete comment",
        });
      },
    });
  }
}
