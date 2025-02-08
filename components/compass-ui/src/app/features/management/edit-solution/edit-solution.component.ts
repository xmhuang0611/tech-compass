import { Component, OnInit } from "@angular/core";
import { FormBuilder, FormGroup, Validators } from "@angular/forms";
import { ActivatedRoute, Router } from "@angular/router";
import { MessageService } from "primeng/api";
import { SolutionService } from "../../../core/services/solution.service";
import { Solution } from "../../../shared/interfaces/solution.interface";

@Component({
  selector: "tc-edit-solution",
  templateUrl: "./edit-solution.component.html",
  styleUrls: ["./edit-solution.component.scss"],
  providers: [MessageService],
})
export class EditSolutionComponent implements OnInit {
  solutionForm: FormGroup;
  loading = false;
  slug!: string;

  constructor(
    private fb: FormBuilder,
    private route: ActivatedRoute,
    private router: Router,
    private solutionService: SolutionService,
    private messageService: MessageService
  ) {
    this.solutionForm = this.fb.group({
      name: ["", Validators.required],
      description: ["", Validators.required],
      brief: ["", Validators.required],
      logo: [""],
      category: ["", Validators.required],
      department: ["", Validators.required],
      team: ["", Validators.required],
      team_email: ["", [Validators.required, Validators.email]],
      maintainer_id: ["", Validators.required],
      maintainer_name: ["", Validators.required],
      maintainer_email: ["", [Validators.required, Validators.email]],
      official_website: [""],
      documentation_url: [""],
      demo_url: [""],
      version: [""],
      adoption_level: ["", Validators.required],
      adoption_user_count: [0, [Validators.required, Validators.min(0)]],
      tags: [[]],
      pros: [[]],
      cons: [[]],
      stage: ["", Validators.required],
      recommend_status: ["", Validators.required],
    });
  }

  ngOnInit() {
    this.slug = this.route.snapshot.params["slug"];
    this.loadSolution();
  }

  private loadSolution() {
    this.loading = true;
    this.solutionService.getMySolutions(0, 1).subscribe({
      next: (response) => {
        const solution = response.data.find((s) => s.slug === this.slug);
        if (solution) {
          this.solutionForm.patchValue(solution);
        } else {
          this.messageService.add({
            severity: "error",
            summary: "Error",
            detail: "Solution not found",
          });
          this.router.navigate(["/manage/solutions"]);
        }
        this.loading = false;
      },
      error: (error) => {
        console.error("Error loading solution:", error);
        this.messageService.add({
          severity: "error",
          summary: "Error",
          detail: "Failed to load solution",
        });
        this.loading = false;
      },
    });
  }

  onSubmit() {
    if (this.solutionForm.valid) {
      this.loading = true;
      const formData = this.solutionForm.value;

      this.solutionService.updateSolution(this.slug, formData).subscribe({
        next: (response) => {
          this.messageService.add({
            severity: "success",
            summary: "Success",
            detail: "Solution updated successfully",
          });
          this.router.navigate(["/manage/solutions"]);
          this.loading = false;
        },
        error: (error) => {
          console.error("Error updating solution:", error);
          this.messageService.add({
            severity: "error",
            summary: "Error",
            detail: "Failed to update solution",
          });
          this.loading = false;
        },
      });
    }
  }
}
