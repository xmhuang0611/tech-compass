import { NgModule } from "@angular/core";
import { CommonModule } from "@angular/common";
import { RouterModule, Routes } from "@angular/router";
import { ReactiveFormsModule } from "@angular/forms";
import { BreadcrumbModule } from "primeng/breadcrumb";
import { MenuModule } from "primeng/menu";
import { CardModule } from "primeng/card";
import { ButtonModule } from "primeng/button";
import { TableModule } from "primeng/table";
import { ChipModule } from "primeng/chip";
import { TagModule } from "primeng/tag";
import { ConfirmDialogModule } from "primeng/confirmdialog";
import { ToastModule } from "primeng/toast";
import { InputTextModule } from "primeng/inputtext";
import { InputTextareaModule } from "primeng/inputtextarea";
import { DropdownModule } from "primeng/dropdown";
import { InputNumberModule } from "primeng/inputnumber";
import { ChipsModule } from "primeng/chips";

import { ManagementLayoutComponent } from "./management-layout/management-layout.component";
import { ManagementDashboardComponent } from "./management-dashboard/management-dashboard.component";
import { MySolutionsComponent } from "./my-solutions/my-solutions.component";
import { EditSolutionComponent } from "./edit-solution/edit-solution.component";
import { MyCommentsComponent } from "./my-comments/my-comments.component";
import { MyRatingsComponent } from "./my-ratings/my-ratings.component";

const routes: Routes = [
  {
    path: "",
    component: ManagementLayoutComponent,
    children: [
      {
        path: "",
        component: ManagementDashboardComponent,
        data: { breadcrumb: "Dashboard" },
      },
      {
        path: "solutions",
        data: { breadcrumb: "My Solutions" },
        children: [
          {
            path: "",
            component: MySolutionsComponent,
          },
          {
            path: "edit/:slug",
            component: EditSolutionComponent,
            data: { breadcrumb: "Edit Solution" },
          },
        ],
      },
      {
        path: "my-comments",
        component: MyCommentsComponent,
        data: { breadcrumb: "My Comments" },
      },
      {
        path: "my-ratings",
        component: MyRatingsComponent,
        data: { breadcrumb: "My Ratings" },
      },
    ],
  },
];

@NgModule({
  declarations: [ManagementLayoutComponent, ManagementDashboardComponent],
  imports: [
    CommonModule,
    RouterModule.forChild(routes),
    ReactiveFormsModule,
    BreadcrumbModule,
    MenuModule,
    CardModule,
    ButtonModule,
    TableModule,
    ChipModule,
    TagModule,
    ConfirmDialogModule,
    ToastModule,
    InputTextModule,
    InputTextareaModule,
    DropdownModule,
    InputNumberModule,
    ChipsModule,
    EditSolutionComponent,
    MySolutionsComponent,
    MyCommentsComponent,
    MyRatingsComponent,
  ],
})
export class ManagementModule {}
