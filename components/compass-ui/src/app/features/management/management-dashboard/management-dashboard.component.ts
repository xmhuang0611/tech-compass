import { Component, OnInit } from "@angular/core";
import { SolutionService } from "../../../core/services/solution.service";
import { CommentService } from "../../../core/services/comment.service";
import { RatingService } from "../../../core/services/rating.service";

interface DashboardStats {
  solutions: number;
  comments: number;
  ratings: number;
  totalSolutions: number;
  totalComments: number;
  totalRatings: number;
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
    totalSolutions: 0,
    totalComments: 0,
    totalRatings: 0,
  };

  constructor(
    private solutionService: SolutionService,
    private commentService: CommentService,
    private ratingService: RatingService
  ) {}

  ngOnInit() {
    this.loadStats();
  }

  private loadStats() {
    // Load my solution count
    this.solutionService.getMySolutions(0, 1).subscribe({
      next: (response) => {
        this.stats.solutions = response.total || 0;
      },
      error: (error) => {
        console.error("Error loading solution count:", error);
      },
    });

    // Load my comments count
    this.commentService.getMyComments(0, 1).subscribe({
      next: (response) => {
        this.stats.comments = response.total || 0;
      },
      error: (error) => {
        console.error("Error loading comments count:", error);
      },
    });

    // Load my ratings count
    this.ratingService.getMyRatings(0, 1).subscribe({
      next: (response) => {
        this.stats.ratings = response.total || 0;
      },
      error: (error) => {
        console.error("Error loading ratings count:", error);
      },
    });

    // Load total solutions count
    this.solutionService.getAllSolutions(0, 1).subscribe({
      next: (response) => {
        this.stats.totalSolutions = response.total || 0;
      },
      error: (error) => {
        console.error("Error loading total solutions count:", error);
      },
    });

    // Load total comments count
    this.commentService.getAllComments(0, 1).subscribe({
      next: (response) => {
        this.stats.totalComments = response.total || 0;
      },
      error: (error) => {
        console.error("Error loading total comments count:", error);
      },
    });

    // Load total ratings count
    this.ratingService.getAllRatings(0, 1).subscribe({
      next: (response) => {
        this.stats.totalRatings = response.total || 0;
      },
      error: (error) => {
        console.error("Error loading total ratings count:", error);
      },
    });
  }
}
