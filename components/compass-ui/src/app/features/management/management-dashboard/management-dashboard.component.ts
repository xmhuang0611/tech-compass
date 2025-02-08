import { Component, OnInit } from "@angular/core";
import { SolutionService } from "../../../core/services/solution.service";
import { CommentService } from "../../../core/services/comment.service";

interface DashboardStats {
  solutions: number;
  comments: number;
  ratings: number;
}

@Component({
  selector: "tc-management-dashboard",
  templateUrl: "./management-dashboard.component.html",
  styleUrls: ["./management-dashboard.component.scss"],
})
export class ManagementDashboardComponent implements OnInit {
  stats: DashboardStats = {
    solutions: 0,
    comments: 0,
    ratings: 0,
  };

  constructor(
    private solutionService: SolutionService,
    private commentService: CommentService
  ) {}

  ngOnInit() {
    this.loadStats();
  }

  private loadStats() {
    // Load solution count
    this.solutionService.getMySolutions(0, 1).subscribe({
      next: (response) => {
        this.stats.solutions = response.total || 0;
      },
      error: (error) => {
        console.error("Error loading solution count:", error);
      },
    });

    // Load comments count
    this.commentService.getMyComments(1, 1).subscribe({
      next: (response) => {
        this.stats.comments = response.total || 0;
      },
      error: (error) => {
        console.error("Error loading comments count:", error);
      },
    });
  }
}
