import { Component, OnInit, OnDestroy } from "@angular/core";
import { CommonModule } from "@angular/common";
import { FormsModule } from "@angular/forms";
import { RouterModule } from "@angular/router";
import { MessageService } from "primeng/api";
import {
  CategoryService,
  Category,
} from "../../../core/services/category.service";
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
import { RadioButtonModule } from "primeng/radiobutton";
import { InputTextModule } from "primeng/inputtext";
import { DropdownModule } from "primeng/dropdown";
import { InputNumberModule } from "primeng/inputnumber";

@Component({
  selector: "app-all-categories",
  templateUrl: "./all-categories.component.html",
  styleUrls: ["./all-categories.component.scss"],
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
    InputNumberModule,
  ],
  providers: [MessageService, ConfirmationService],
})
export class AllCategoriesComponent implements OnInit, OnDestroy {
  categories: Category[] = [];
  loading = false;
  totalRecords = 0;
  pageSize = 10;
  currentPage = 0;
  rowsPerPageOptions: number[] = [5, 10, 20, 50];

  editDialogVisible = false;
  editingCategory: Partial<Category> = {};

  private destroy$ = new Subject<void>();

  constructor(
    private categoryService: CategoryService,
    private messageService: MessageService,
    private confirmationService: ConfirmationService
  ) {}

  ngOnInit() {
    this.loadCategories();
  }

  ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
  }

  loadCategories() {
    this.loading = true;
    const skip = this.currentPage * this.pageSize;

    this.categoryService
      .getAllCategories(skip, this.pageSize)
      .pipe(
        finalize(() => {
          this.loading = false;
        })
      )
      .subscribe({
        next: (response) => {
          if (response.success) {
            this.categories = response.data;
            this.totalRecords = response.total;
          }
        },
        error: (error) => {
          this.messageService.add({
            severity: "error",
            summary: "Error",
            detail: "Failed to load categories",
          });
        },
      });
  }

  onPageChange(event: any) {
    this.pageSize = event.rows;
    this.currentPage = Math.floor(event.first / event.rows);
    this.loadCategories();
  }

  editCategory(category: Category) {
    this.editingCategory = { ...category };
    this.editDialogVisible = true;
  }

  saveCategory() {
    if (!this.editingCategory._id || !this.editingCategory.name?.trim()) {
      return;
    }

    this.loading = true;
    this.categoryService
      .updateCategory(this.editingCategory._id, {
        name: this.editingCategory.name,
        description: this.editingCategory.description || "",
        radar_quadrant: this.editingCategory.radar_quadrant ?? -1
      })
      .subscribe({
        next: (response) => {
          if (response.success) {
            this.messageService.add({
              severity: "success",
              summary: "Success",
              detail: "Category updated successfully",
            });
            this.editDialogVisible = false;
            this.loadCategories();
          }
          this.loading = false;
        },
        error: (error) => {
          this.messageService.add({
            severity: "error",
            summary: "Error",
            detail: error.error?.detail || "Failed to update category",
          });
          this.loading = false;
        },
      });
  }

  confirmDelete(category: Category) {
    this.confirmationService.confirm({
      message: "Are you sure you want to delete this category?",
      accept: () => {
        this.deleteCategory(category);
      },
    });
  }

  private deleteCategory(category: Category) {
    this.loading = true;

    this.categoryService.deleteCategory(category._id).subscribe({
      next: (response) => {
        this.messageService.add({
          severity: "success",
          summary: "Success",
          detail: "Category deleted successfully",
        });
        this.loadCategories();
      },
      error: (error) => {
        this.messageService.add({
          severity: "error",
          summary: "Error",
          detail: error.error?.detail || "Failed to delete category",
        });
        this.loading = false;
      },
    });
  }
} 