import { Component, OnInit } from "@angular/core";
import { Router } from "@angular/router";
import { ConfirmationService, MessageService } from "primeng/api";
import { SolutionService } from "../../../core/services/solution.service";
import { Solution } from "../../../shared/interfaces/solution.interface";

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
})
export class MySolutionsComponent implements OnInit {
  solutions: Solution[] = [];
  totalRecords: number = 0;
  loading: boolean = true;
  first: number = 0;
  rows: number = 10;

  constructor(
    private solutionService: SolutionService,
    private router: Router,
    private confirmationService: ConfirmationService,
    private messageService: MessageService
  ) {}

  ngOnInit() {
    this.loadSolutions();
  }

  loadSolutions(event?: any) {
    this.loading = true;
    const skip = event?.first || 0;
    const limit = event?.rows || this.rows;

    this.solutionService.getMySolutions(skip, limit).subscribe({
      next: (response) => {
        this.solutions = response.data;
        this.totalRecords = response.total || 0;
        this.loading = false;
      },
      error: (error) => {
        console.error("Error loading solutions:", error);
        this.loading = false;
      },
    });
  }

  onPageChange(event: any) {
    this.first = event.first;
    this.rows = event.rows;
    this.loadSolutions(event);
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
        this.loadSolutions();
      },
      error: (error) => {
        console.error("Error deleting solution:", error);
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
      // Recommendation status
      ADOPT: "success",
      TRIAL: "info",
      ASSESS: "warning",
      HOLD: "danger",
      // Review status
      PENDING: "warning",
      APPROVED: "success",
      REJECTED: "danger",
    };
    return severityMap[status] || "secondary";
  }
}
