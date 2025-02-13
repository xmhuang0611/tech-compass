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
import { AuthService } from "../../../core/services/auth.service";
import { take } from "rxjs/operators";

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
import { StandardResponse } from "../../../core/interfaces/standard-response.interface";

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
  isAdmin = false;

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

  reviewStatusOptions = [
    { label: "PENDING", value: "PENDING" },
    { label: "APPROVED", value: "APPROVED" },
    { label: "REJECTED", value: "REJECTED" },
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
    private messageService: MessageService,
    private authService: AuthService
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
      recommend_status: [{ value: "", disabled: true }],
      review_status: [{ value: "", disabled: true }],
      adoption_level: ["", Validators.required],
      adoption_user_count: [0, [Validators.required, Validators.min(0)]],
    });
  }

  ngOnInit() {
    this.loadCategories();
    this.loadDepartments();
    this.checkAdminStatus();
    this.loadSolution();
  }

  private checkAdminStatus() {
    this.authService.currentUser$.pipe(take(1)).subscribe((user) => {
      this.isAdmin = user?.is_superuser || false;
      if (this.isAdmin) {
        this.solutionForm.get("recommend_status")?.enable();
        this.solutionForm.get("review_status")?.enable();
      }
    });
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
    if (!this.slug) {
      this.messageService.add({
        severity: "error",
        summary: "Error",
        detail: "No solution slug provided",
      });
      this.router.navigate(["/manage/my-solutions"]);
      return;
    }

    this.loading = true;
    this.solutionService.getSolution(this.slug).subscribe({
      next: (response: StandardResponse<Solution>) => {
        if (response.success && response.data) {
          // Convert arrays back to newline-separated strings for pros and cons
          const formValue = {
            ...response.data,
            pros: response.data.pros?.join("\n") || "",
            cons: response.data.cons?.join("\n") || "",
          };
          this.solutionForm.patchValue(formValue);
          this.loading = false;
        } else {
          this.messageService.add({
            severity: "error",
            summary: "Error",
            detail: "Failed to load solution",
          });
          this.router.navigate(["/manage/my-solutions"]);
        }
      },
      error: (error: { error?: { detail: string } }) => {
        this.messageService.add({
          severity: "error",
          summary: "Error",
          detail: error.error?.detail || "Failed to load solution",
        });
        this.router.navigate(["/manage/my-solutions"]);
        this.loading = false;
      },
    });
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

      // Create solution object, excluding admin-only fields for non-admins
      const { recommend_status, review_status, ...baseData } = formValue;
      let solutionData = {
        ...baseData,
        pros,
        cons,
      };

      // Only include admin fields if user is admin
      if (this.isAdmin) {
        solutionData = {
          ...solutionData,
          recommend_status,
          review_status,
        };
      }

      this.solutionService.updateSolution(this.slug, solutionData).subscribe({
        next: (response) => {
          if (response.success) {
            this.messageService.add({
              severity: "success",
              summary: "Success",
              detail: "Solution updated successfully",
              life: 3000,
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
