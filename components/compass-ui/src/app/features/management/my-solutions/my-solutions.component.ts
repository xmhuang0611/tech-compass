import { Component, OnInit, ViewChild, ElementRef } from "@angular/core";
import { CommonModule } from "@angular/common";
import { RouterModule } from "@angular/router";
import { FormsModule } from "@angular/forms";
import { Router, ActivatedRoute } from "@angular/router";
import { ConfirmationService, MessageService } from "primeng/api";
import { SolutionService } from "../../../core/services/solution.service";
import { Solution } from "../../../shared/interfaces/solution.interface";
import { RatingModule } from "primeng/rating";
import { TableModule } from "primeng/table";
import { ButtonModule } from "primeng/button";
import { TagModule } from "primeng/tag";
import { ConfirmDialogModule } from "primeng/confirmdialog";

type TagSeverity =
  | "success"
  | "info"
  | "warning"
  | "danger"
  | "secondary"
  | "contrast";

@Component({
  selector: "tc-my-solutions",
  templateUrl: "./my-solutions.component.html",
  styleUrls: ["./my-solutions.component.scss"],
  providers: [ConfirmationService, MessageService],
  imports: [
    CommonModule,
    RouterModule,
    FormsModule,
    RatingModule,
    TableModule,
    ButtonModule,
    TagModule,
    ConfirmDialogModule,
  ],
  standalone: true,
})
export class MySolutionsComponent implements OnInit {
  @ViewChild("scrollContainer") scrollContainer!: ElementRef;

  solutions: Solution[] = [];
  totalRecords: number = 0;
  loading: boolean = true;
  pageSize: number = 10;
  currentPage: number = 0;
  rowsPerPageOptions: number[] = [5, 10, 20, 50];

  constructor(
    private solutionService: SolutionService,
    private router: Router,
    private route: ActivatedRoute,
    private confirmationService: ConfirmationService,
    private messageService: MessageService
  ) {}

  ngOnInit() {
    this.loadSolutions();
  }

  loadSolutions() {
    this.loading = true;
    const skip = this.currentPage * this.pageSize;

    this.solutionService.getMySolutions(skip, this.pageSize).subscribe({
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
    this.router.navigate(["/manage/my-solutions/edit", solution.slug], {
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
