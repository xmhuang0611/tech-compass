import { Component, OnInit, OnDestroy } from "@angular/core";
import { CommonModule } from "@angular/common";
import { FormsModule } from "@angular/forms";
import { RouterModule } from "@angular/router";
import { MessageService } from "primeng/api";
import {
  CommentService,
  Comment,
} from "../../../core/services/comment.service";
import { BehaviorSubject, Subject, debounceTime, takeUntil, finalize } from "rxjs";

// PrimeNG Components
import { ButtonModule } from "primeng/button";
import { TableModule } from "primeng/table";
import { ToastModule } from "primeng/toast";
import { DialogModule } from "primeng/dialog";
import { InputTextareaModule } from "primeng/inputtextarea";
import { ConfirmDialogModule } from "primeng/confirmdialog";
import { ConfirmationService } from "primeng/api";
import { TagModule } from "primeng/tag";
import { RadioButtonModule } from "primeng/radiobutton";
import { InputTextModule } from "primeng/inputtext";
import { DropdownModule } from "primeng/dropdown";

@Component({
  selector: "app-all-comments",
  templateUrl: "./all-comments.component.html",
  styleUrls: ["./all-comments.component.scss"],
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
    TagModule,
    RadioButtonModule,
    InputTextModule,
    DropdownModule,
  ],
  providers: [MessageService, ConfirmationService],
})
export class AllCommentsComponent implements OnInit, OnDestroy {
  comments: Comment[] = [];
  loading = false;
  totalRecords = 0;
  pageSize = 10;
  currentPage = 0;
  rowsPerPageOptions: number[] = [5, 10, 20, 50];

  editDialogVisible = false;
  editingComment: Partial<Comment> = {};

  commentTypes = [
    { label: "Official Comment", value: "OFFICIAL" },
    { label: "User Comment", value: "USER" },
  ];

  // Filters
  filters: {
    solution_slug: string;
    type: "OFFICIAL" | "USER" | "";
  } = {
    solution_slug: "",
    type: "",
  };

  private destroy$ = new Subject<void>();
  private searchSubject = new Subject<void>();

  constructor(
    private commentService: CommentService,
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
    this.loadComments();
  }

  ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
  }

  onFilterChange() {
    this.searchSubject.next();
  }

  getCommentTypeSeverity(type: string): "success" | "info" | "warning" | "danger" {
    switch (type) {
      case "OFFICIAL":
        return "success";
      case "USER":
        return "info";
      default:
        return "info";
    }
  }

  loadComments() {
    this.loading = true;
    const skip = this.currentPage * this.pageSize;

    const filters = {
      solution_slug: this.filters.solution_slug || undefined,
      type: this.filters.type || undefined
    };

    this.commentService
      .getAllComments(skip, this.pageSize, filters)
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
    if (!this.editingComment._id || !this.editingComment.content?.trim() || !this.editingComment.type) {
      return;
    }

    this.loading = true;
    this.commentService
      .updateComment(this.editingComment._id, this.editingComment.content, this.editingComment.type)
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