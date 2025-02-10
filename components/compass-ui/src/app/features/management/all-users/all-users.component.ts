import { Component, OnInit, OnDestroy } from "@angular/core";
import { CommonModule } from "@angular/common";
import { FormsModule } from "@angular/forms";
import { RouterModule } from "@angular/router";
import { MessageService } from "primeng/api";
import { UserService, User, UserResponse } from "../../../core/services/user.service";
import { Subject, debounceTime, takeUntil, finalize } from "rxjs";

// PrimeNG Components
import { ButtonModule } from "primeng/button";
import { TableModule } from "primeng/table";
import { ToastModule } from "primeng/toast";
import { DialogModule } from "primeng/dialog";
import { InputTextModule } from "primeng/inputtext";
import { DropdownModule } from "primeng/dropdown";
import { TagModule } from "primeng/tag";
import { CheckboxModule } from "primeng/checkbox";

@Component({
  selector: "app-all-users",
  templateUrl: "./all-users.component.html",
  styleUrls: ["./all-users.component.scss"],
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    RouterModule,
    ButtonModule,
    TableModule,
    ToastModule,
    DialogModule,
    InputTextModule,
    DropdownModule,
    TagModule,
    CheckboxModule,
  ],
  providers: [MessageService],
})
export class AllUsersComponent implements OnInit, OnDestroy {
  users: User[] = [];
  loading = false;
  totalRecords = 0;
  pageSize = 10;
  currentPage = 0;
  rowsPerPageOptions: number[] = [5, 10, 20, 50];

  editDialogVisible = false;
  editingUser: Partial<User> = {};

  // Filters
  filters = {
    username: "",
    is_active: null as boolean | null,
    is_superuser: null as boolean | null,
  };

  statusOptions = [
    { label: "All Status", value: null },
    { label: "Active", value: true },
    { label: "Inactive", value: false },
  ];

  roleOptions = [
    { label: "All Roles", value: null },
    { label: "Admin", value: true },
    { label: "User", value: false },
  ];

  private destroy$ = new Subject<void>();
  private searchSubject = new Subject<void>();

  constructor(
    private userService: UserService,
    private messageService: MessageService
  ) {
    // Setup search debounce
    this.searchSubject
      .pipe(debounceTime(300), takeUntil(this.destroy$))
      .subscribe(() => {
        this.resetAndReload();
      });
  }

  ngOnInit() {
    this.loadUsers();
  }

  ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
  }

  onFilterChange() {
    this.searchSubject.next();
  }

  loadUsers() {
    this.loading = true;
    const skip = this.currentPage * this.pageSize;

    // Create a type-safe filters object
    const apiFilters: {
      username?: string;
      is_active?: boolean;
      is_superuser?: boolean;
    } = {};

    if (this.filters.username) {
      apiFilters.username = this.filters.username;
    }
    if (this.filters.is_active !== null) {
      apiFilters.is_active = this.filters.is_active;
    }
    if (this.filters.is_superuser !== null) {
      apiFilters.is_superuser = this.filters.is_superuser;
    }

    this.userService
      .getAllUsers(skip, this.pageSize, apiFilters)
      .pipe(
        finalize(() => {
          this.loading = false;
        })
      )
      .subscribe({
        next: (response: UserResponse) => {
          if (response.success) {
            this.users = response.data;
            this.totalRecords = response.total;
          }
        },
        error: (error: any) => {
          this.messageService.add({
            severity: "error",
            summary: "Error",
            detail: "Failed to load users",
          });
        },
      });
  }

  private resetAndReload() {
    this.currentPage = 0;
    this.users = [];
    this.loadUsers();
  }

  onPageChange(event: any) {
    this.pageSize = event.rows;
    this.currentPage = Math.floor(event.first / event.rows);
    this.loadUsers();
  }

  getStatusSeverity(isActive: boolean): "success" | "danger" {
    return isActive ? "success" : "danger";
  }

  getRoleSeverity(isSuperuser: boolean): "warning" | "info" {
    return isSuperuser ? "warning" : "info";
  }

  editUser(user: User) {
    this.editingUser = { ...user };
    this.editDialogVisible = true;
  }

  saveUser() {
    if (!this.editingUser.username) {
      return;
    }

    this.loading = true;
    this.userService
      .updateUser(this.editingUser.username, {
        is_active: this.editingUser.is_active || false,
        is_superuser: this.editingUser.is_superuser || false,
      })
      .subscribe({
        next: (response) => {
          this.messageService.add({
            severity: "success",
            summary: "Success",
            detail: "User updated successfully",
          });
          this.editDialogVisible = false;
          this.loadUsers();
          this.loading = false;
        },
        error: (error: any) => {
          this.messageService.add({
            severity: "error",
            summary: "Error",
            detail: error.error?.detail || "Failed to update user",
          });
          this.loading = false;
        },
      });
  }
} 