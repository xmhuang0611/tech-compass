import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Routes } from '@angular/router';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';

import { BreadcrumbModule } from 'primeng/breadcrumb';
import { ButtonModule } from 'primeng/button';
import { ChipsModule } from 'primeng/chips';
import { DialogService, DynamicDialogModule } from 'primeng/dynamicdialog';
import { DropdownModule } from 'primeng/dropdown';
import { InputTextModule } from 'primeng/inputtext';
import { InputTextareaModule } from 'primeng/inputtextarea';
import { MessagesModule } from 'primeng/messages';

import { SubmitSuccessComponent } from './submit-success.component';

const routes: Routes = [
  {
    path: '',
    loadComponent: () => import('./submit-solution.component').then(m => m.SubmitSolutionComponent)
  },
  {
    path: 'success',
    component: SubmitSuccessComponent
  }
];

@NgModule({
  declarations: [
    SubmitSuccessComponent
  ],
  imports: [
    CommonModule,
    RouterModule.forChild(routes),
    FormsModule,
    ReactiveFormsModule,
    BreadcrumbModule,
    ButtonModule,
    ChipsModule,
    DynamicDialogModule,
    DropdownModule,
    InputTextModule,
    InputTextareaModule,
    MessagesModule
  ],
  providers: [
    DialogService
  ]
})
export class SubmitSolutionModule { }
