import { Component, OnInit, ViewChild, ElementRef } from "@angular/core";
import { CommonModule } from "@angular/common";
import { RouterModule } from "@angular/router";
import { FormsModule } from "@angular/forms";
import { Router, ActivatedRoute } from "@angular/router";
import { SolutionService } from "../../../core/services/solution.service";
import { CategoryService } from "../../../core/services/category.service";
import { Solution } from "../../../shared/interfaces/solution.interface";
import { ConfirmationService, MessageService } from "primeng/api";
import { RatingModule } from "primeng/rating";
import { TableModule } from "primeng/table";
import { ButtonModule } from "primeng/button";
import { TagModule } from "primeng/tag";
import { DropdownModule } from "primeng/dropdown";
import { TooltipModule } from "primeng/tooltip";
import { ConfirmDialogModule } from "primeng/confirmdialog";
import { MessagesModule } from "primeng/messages";

type TagSeverity =
  | "success"
  | "info"
  | "warning"
  | "danger"
  | "secondary"
  | "contrast";

interface Filters {
  category?: string;
  recommend_status?: string;
  review_status?: string;
}

@Component({
  selector: "tc-all-solutions",
  templateUrl: "./all-solutions.component.html",
  styleUrls: ["./all-solutions.component.scss"],
  imports: [
    CommonModule,
    RouterModule,
    FormsModule,
    RatingModule,
    TableModule,
    ButtonModule,
    TagModule,
    DropdownModule,
    TooltipModule,
    ConfirmDialogModule,
    MessagesModule,
  ],
  standalone: true,
  providers: [ConfirmationService, MessageService],
})
export class AllSolutionsComponent implements OnInit {
  @ViewChild("scrollContainer") scrollContainer!: ElementRef;

  solutions: Solution[] = [];
  categories: { name: string }[] = [];
  totalRecords: number = 0;
  loading: boolean = true;
  pageSize: number = 10;
  currentPage: number = 0;
  rowsPerPageOptions: number[] = [5, 10, 20, 50];

  filters: Filters = {};

  recommendStatusOptions = [
    { label: "ADOPT", value: "ADOPT" },
    { label: "TRIAL", value: "TRIAL" },
    { label: "ASSESS", value: "ASSESS" },
    { label: "HOLD", value: "HOLD" },
  ];

  reviewStatusOptions = [
    { label: "PENDING", value: "PENDING" },
    { label: "APPROVED", value: "APPROVED" },
    { label: "REJECTED", value: "REJECTED" },
  ];

  constructor(
    private solutionService: SolutionService,
    private categoryService: CategoryService,
    private router: Router,
    private route: ActivatedRoute,
    private confirmationService: ConfirmationService,
    private messageService: MessageService
  ) {}

  ngOnInit() {
    this.loadCategories();
    this.loadSolutions();
  }

  private loadCategories() {
    this.categoryService.getCategories().subscribe({
      next: (response) => {
        if (response.success) {
          this.categories = response.data;
        }
      },
      error: () => {
        this.messageService.add({
          severity: "error",
          summary: "Error",
          detail: "Failed to load categories",
        });
      },
    });
  }

  loadSolutions() {
    this.loading = true;
    const skip = this.currentPage * this.pageSize;

    this.solutionService
      .getAllSolutions(skip, this.pageSize, undefined, this.filters)
      .subscribe({
        next: (response) => {
          this.solutions = response.data;
          this.totalRecords = response.total;
          this.loading = false;
        },
        error: (error) => {
          this.messageService.add({
            severity: "error",
            summary: "Error",
            detail: "Failed to load solutions",
          });
          this.loading = false;
        },
      });
  }

  onFilterChange() {
    this.currentPage = 0;
    this.loadSolutions();
  }

  onPageChange(event: any) {
    this.pageSize = event.rows;
    this.currentPage = Math.floor(event.first / event.rows);
    this.loadSolutions();
  }

  private resetAndReload() {
    this.currentPage = 0;
    this.solutions = [];
    this.loadSolutions();
  }

  editSolution(solution: Solution) {
    this.router.navigate(["edit", solution.slug], {
      relativeTo: this.route,
      state: { solution },
    });
  }

  confirmDelete(solution: Solution) {
    this.confirmationService.confirm({
      message: `Are you sure you want to delete "${solution.name}"?`,
      accept: () => {
        this.deleteSolution(solution);
      },
    });
  }

  private deleteSolution(solution: Solution) {
    this.loading = true;
    this.solutionService.deleteSolution(solution.slug).subscribe({
      next: () => {
        this.messageService.add({
          severity: "success",
          summary: "Success",
          detail: "Solution deleted successfully",
        });
        this.resetAndReload();
      },
      error: (error) => {
        this.messageService.add({
          severity: "error",
          summary: "Error",
          detail: "Failed to delete solution",
        });
        this.loading = false;
      },
    });
  }

  viewSolution(slug: string) {
    this.router.navigate(["/solutions", slug]);
  }

  getStatusSeverity(status: string): TagSeverity {
    const severityMap: { [key: string]: TagSeverity } = {
      ADOPT: "success",
      TRIAL: "info",
      ASSESS: "warning",
      HOLD: "danger",
      PENDING: "warning",
      APPROVED: "success",
      REJECTED: "danger",
    };
    return severityMap[status] || "secondary";
  }
}
