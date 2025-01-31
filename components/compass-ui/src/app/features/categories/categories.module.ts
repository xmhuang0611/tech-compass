import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Routes } from '@angular/router';
import { TooltipModule } from 'primeng/tooltip';
import { CategoriesComponent } from './categories.component';
import { CategoryService } from './category.service';

const routes: Routes = [
  { path: '', component: CategoriesComponent }
];

@NgModule({
  declarations: [],
  imports: [
    CommonModule,
    RouterModule.forChild(routes),
    TooltipModule
  ],
  providers: [CategoryService]
})
export class CategoriesModule { }