import { Component, OnInit, OnDestroy } from "@angular/core";
import { CommonModule } from "@angular/common";
import { FormsModule } from "@angular/forms";
import { RouterModule } from "@angular/router";
import { MessageService } from "primeng/api";
import { TagService, Tag } from "../../../core/services/tag.service";
import { Subject, finalize } from "rxjs";

// PrimeNG Components
import { ButtonModule } from "primeng/button";
import { TableModule } from "primeng/table";
import { ToastModule } from "primeng/toast";
import { DialogModule } from "primeng/dialog";
import { InputTextareaModule } from "primeng/inputtextarea";
import { ConfirmDialogModule } from "primeng/confirmdialog";
import { ConfirmationService } from "primeng/api";
import { TagModule } from "primeng/tag";
import { InputTextModule } from "primeng/inputtext";

@Component({
  selector: "app-all-tags",
  templateUrl: "./all-tags.component.html",
  styleUrls: ["./all-tags.component.scss"],
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
    InputTextModule,
  ],
  providers: [MessageService, ConfirmationService],
})
export class AllTagsComponent implements OnInit, OnDestroy {
  tags: Tag[] = [];
  loading = false;
  totalRecords = 0;
  pageSize = 10;
  currentPage = 0;
  rowsPerPageOptions: number[] = [5, 10, 20, 50];

  editDialogVisible = false;
  editingTag: Partial<Tag> = {};
  tagToDelete: Tag | null = null;

  private destroy$ = new Subject<void>();

  constructor(
    private tagService: TagService,
    private messageService: MessageService,
    private confirmationService: ConfirmationService
  ) {}

  ngOnInit() {
    this.loadTags();
  }

  ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
  }

  loadTags() {
    this.loading = true;
    const skip = this.currentPage * this.pageSize;

    if (this.currentPage === 0 && this.pageSize >= 50) {
      // Use getTags() for the first page when requesting 50 or more items
      this.tagService
        .getTags()
        .pipe(
          finalize(() => {
            this.loading = false;
          })
        )
        .subscribe({
          next: (response) => {
            if (response.success) {
              this.tags = response.data;
              this.totalRecords = response.total;
            }
          },
          error: (error) => {
            this.messageService.add({
              severity: "error",
              summary: "Error",
              detail: "Failed to load tags",
            });
          },
        });
    } else {
      // Use getAllTags() for pagination
      this.tagService
        .getAllTags(skip, this.pageSize)
        .pipe(
          finalize(() => {
            this.loading = false;
          })
        )
        .subscribe({
          next: (response) => {
            if (response.success) {
              this.tags = response.data;
              this.totalRecords = response.total;
            }
          },
          error: (error) => {
            this.messageService.add({
              severity: "error",
              summary: "Error",
              detail: "Failed to load tags",
            });
          },
        });
    }
  }

  onPageChange(event: any) {
    this.pageSize = event.rows;
    this.currentPage = Math.floor(event.first / event.rows);
    this.loadTags();
  }

  editTag(tag: Tag) {
    this.editingTag = { ...tag };
    this.editDialogVisible = true;
  }

  saveTag() {
    if (!this.editingTag._id || !this.editingTag.name?.trim()) {
      return;
    }

    this.loading = true;
    this.tagService
      .updateTag(this.editingTag._id, {
        name: this.editingTag.name,
        description: this.editingTag.description || "",
      })
      .subscribe({
        next: (response) => {
          if (response.success) {
            this.messageService.add({
              severity: "success",
              summary: "Success",
              detail: "Tag updated successfully",
            });
            this.editDialogVisible = false;
            this.loadTags();
          }
          this.loading = false;
        },
        error: (error) => {
          this.messageService.add({
            severity: "error",
            summary: "Error",
            detail: error.error?.detail || "Failed to update tag",
          });
          this.loading = false;
        },
      });
  }

  confirmDelete(tag: Tag) {
    this.tagToDelete = tag;
    this.confirmationService.confirm({
      accept: () => {
        this.deleteTag(tag);
      },
      reject: () => {
        this.tagToDelete = null;
      }
    });
  }

  private deleteTag(tag: Tag) {
    this.loading = true;

    this.tagService.deleteTag(tag._id).subscribe({
      next: (response) => {
        this.messageService.add({
          severity: "success",
          summary: "Success",
          detail: "Tag deleted successfully",
        });
        this.loadTags();
        this.tagToDelete = null;
      },
      error: (error) => {
        this.messageService.add({
          severity: "error",
          summary: "Error",
          detail: error.error?.detail || "Failed to delete tag",
        });
        this.loading = false;
        this.tagToDelete = null;
      },
    });
  }
} 