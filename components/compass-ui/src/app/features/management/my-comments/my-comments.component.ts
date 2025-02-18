import { CommonModule, DatePipe } from "@angular/common";
import { Component, OnInit } from "@angular/core";
import { FormsModule } from "@angular/forms";
import { RouterModule } from "@angular/router";
import { MessageService } from "primeng/api";
import { finalize } from "rxjs";
import {
    Comment,
    CommentService,
} from "../../../core/services/comment.service";

// PrimeNG Components
import { ConfirmationService } from "primeng/api";
import { ButtonModule } from "primeng/button";
import { CheckboxModule } from "primeng/checkbox";
import { ConfirmDialogModule } from "primeng/confirmdialog";
import { DialogModule } from "primeng/dialog";
import { InputTextareaModule } from "primeng/inputtextarea";
import { ProgressSpinnerModule } from "primeng/progressspinner";
import { TableModule } from "primeng/table";
import { ToastModule } from "primeng/toast";

@Component({
  selector: "app-my-comments",
  templateUrl: "./my-comments.component.html",
  styleUrls: ["./my-comments.component.scss"],
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
    TableModule,
    ToastModule,
  ],
  providers: [MessageService, ConfirmationService],
})
export class MyCommentsComponent implements OnInit {
  comments: Comment[] = [];
  loading = false;
  totalRecords = 0;
  pageSize = 10;
  currentPage = 0;
  rowsPerPageOptions: number[] = [5, 10, 20, 50];

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

  loadComments() {
    this.loading = true;
    const skip = this.currentPage * this.pageSize;

    this.commentService
      .getMyComments(skip, this.pageSize)
      .pipe(
        finalize(() => {
          this.loading = false;
        })
      )
      .subscribe({
        next: (response) => {
          if (response.success) {
            this.comments = response.data;
            this.totalRecords = response.total;
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

  private resetAndReload() {
    this.currentPage = 0;
    this.comments = [];
    this.loadComments();
  }

  onPageChange(event: any) {
    this.pageSize = event.rows;
    this.currentPage = Math.floor(event.first / event.rows);
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

    this.loading = true;
    this.commentService
      .updateComment(
        this.editingComment._id,
        this.editingComment.content,
        this.editingComment.type || "USER",
        this.editingComment.is_adopted_user
      )
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
          this.loading = false;
        },
        error: (error) => {
          this.messageService.add({
            severity: "error",
            summary: "Error",
            detail: error.error?.detail || "Failed to update comment",
          });
          this.loading = false;
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

  private deleteComment(comment: Comment) {
    this.loading = true;

    this.commentService.deleteComment(comment._id).subscribe({
      next: (response) => {
        // 204 response will be null, which is expected for successful deletion
        this.messageService.add({
          severity: "success",
          summary: "Success",
          detail: "Comment deleted successfully",
        });
        this.loadComments();
      },
      error: (error) => {
        this.messageService.add({
          severity: "error",
          summary: "Error",
          detail: error.error?.detail || "Failed to delete comment",
        });
        this.loading = false;
      },
    });
  }
}
