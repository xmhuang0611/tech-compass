import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { SolutionsCatalogComponent } from './solutions-catalog/solutions-catalog.component';

const routes: Routes = [
  {
    path: '',
    component: SolutionsCatalogComponent
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class SolutionsRoutingModule { } 