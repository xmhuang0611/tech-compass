import { Component, OnInit } from "@angular/core";
import { CommonModule } from "@angular/common";
import {
  FormBuilder,
  FormGroup,
  Validators,
  FormsModule,
  ReactiveFormsModule,
} from "@angular/forms";
import { ActivatedRoute, Router, RouterModule } from "@angular/router";
import { MessageService } from "primeng/api";

import { ButtonModule } from "primeng/button";
import { ChipsModule } from "primeng/chips";
import { DropdownModule } from "primeng/dropdown";
import { InputTextModule } from "primeng/inputtext";
import { InputTextareaModule } from "primeng/inputtextarea";
import { InputNumberModule } from "primeng/inputnumber";
import { MessagesModule } from "primeng/messages";

import { CategoryService } from "../../../core/services/category.service";
import { DepartmentService } from "../../../core/services/department.service";
import { SolutionService } from "../../../core/services/solution.service";
import { Solution } from "../../../shared/interfaces/solution.interface";

@Component({
  selector: "tc-edit-solution",
  templateUrl: "./edit-solution.component.html",
  styleUrls: ["./edit-solution.component.scss"],
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    RouterModule,
    ButtonModule,
    ChipsModule,
    DropdownModule,
    InputTextModule,
    InputTextareaModule,
    InputNumberModule,
    MessagesModule,
  ],
  providers: [MessageService],
})
export class EditSolutionComponent implements OnInit {
  categories: { name: string }[] = [];
  departments: string[] = [];
  loading = false;
  slug!: string;

  stageOptions = [
    { label: "DEVELOPING", value: "DEVELOPING" },
    { label: "UAT", value: "UAT" },
    { label: "PRODUCTION", value: "PRODUCTION" },
    { label: "DEPRECATED", value: "DEPRECATED" },
    { label: "RETIRED", value: "RETIRED" },
  ];

  recommendStatusOptions = [
    { label: "ADOPT", value: "ADOPT" },
    { label: "TRIAL", value: "TRIAL" },
    { label: "ASSESS", value: "ASSESS" },
    { label: "HOLD", value: "HOLD" },
  ];

  adoptionLevelOptions = [
    { label: "PILOT", value: "PILOT" },
    { label: "TEAM", value: "TEAM" },
    { label: "DEPARTMENT", value: "DEPARTMENT" },
    { label: "ENTERPRISE", value: "ENTERPRISE" },
    { label: "INDUSTRY", value: "INDUSTRY" },
  ];

  solutionForm: FormGroup;

  constructor(
    private fb: FormBuilder,
    private route: ActivatedRoute,
    private router: Router,
    private categoryService: CategoryService,
    private departmentService: DepartmentService,
    private solutionService: SolutionService,
    private messageService: MessageService
  ) {
    this.solutionForm = this.fb.group({
      name: ["", Validators.required],
      brief: ["", [Validators.required, Validators.maxLength(200)]],
      description: ["", Validators.required],
      category: ["", Validators.required],
      logo: [""],
      department: ["", Validators.required],
      team: ["", Validators.required],
      team_email: ["", [Validators.required, Validators.email]],
      maintainer_id: ["", Validators.required],
      maintainer_name: ["", Validators.required],
      maintainer_email: ["", [Validators.required, Validators.email]],
      official_website: [""],
      documentation_url: [""],
      demo_url: [""],
      version: ["", Validators.required],
      tags: [[]],
      pros: ["", Validators.required],
      cons: ["", Validators.required],
      stage: ["", Validators.required],
      recommend_status: [{ value: "", disabled: true }, Validators.required],
      adoption_level: ["", Validators.required],
      adoption_user_count: [0, [Validators.required, Validators.min(0)]],
    });
  }

  ngOnInit() {
    this.loadCategories();
    this.loadDepartments();
    this.loadSolution();
  }

  private loadCategories() {
    this.categoryService.getCategories().subscribe((response) => {
      if (response.success) {
        this.categories = response.data;
      }
    });
  }

  private loadDepartments() {
    this.departmentService.getDepartments().subscribe((response) => {
      if (response.success) {
        this.departments = response.data;
      }
    });
  }

  private loadSolution() {
    this.slug = this.route.snapshot.params["slug"];
    const solution = history.state.solution as Solution;

    if (solution) {
      // Convert arrays back to newline-separated strings for pros and cons
      const formValue = {
        ...solution,
        pros: solution.pros?.join("\n") || "",
        cons: solution.cons?.join("\n") || "",
      };
      this.solutionForm.patchValue(formValue);
    } else {
      this.messageService.add({
        severity: "error",
        summary: "Error",
        detail: "No solution data provided",
      });
      this.router.navigate(["/manage/solutions"]);
    }
  }

  onSubmit() {
    if (this.solutionForm.valid) {
      this.loading = true;

      // Convert multiline text to arrays for pros and cons
      const formValue = this.solutionForm.getRawValue();
      const pros =
        formValue.pros?.split("\n").filter((line: string) => line.trim()) || [];
      const cons =
        formValue.cons?.split("\n").filter((line: string) => line.trim()) || [];

      // Create solution object without recommend_status
      const { recommend_status, ...solutionData } = formValue;
      const solution = {
        ...solutionData,
        pros,
        cons,
      };

      this.solutionService.updateSolution(this.slug, solution).subscribe({
        next: (response) => {
          if (response.success) {
            this.messageService.add({
              severity: "success",
              summary: "Success",
              detail: "Solution updated successfully",
            });
          } else {
            this.messageService.add({
              severity: "error",
              summary: "Error",
              detail: response.detail || "Failed to update solution",
            });
          }
          this.loading = false;
        },
        error: (error) => {
          this.messageService.add({
            severity: "error",
            summary: "Error",
            detail: error.error?.detail || "Failed to update solution",
          });
          this.loading = false;
        },
      });
    }
  }
}
