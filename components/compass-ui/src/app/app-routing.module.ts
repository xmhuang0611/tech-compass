import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

const routes: Routes = [
  {
    path: '',
    children: [
      {
        path: '',
        loadComponent: () => import('./features/home/home.component').then(m => m.HomeComponent)
      },
      {
        path: 'submit-solution',
        loadChildren: () => import('./features/submit-solution/submit-solution.module')
          .then(m => m.SubmitSolutionModule)
      },
      {
        path: 'solution-catalog',
        loadComponent: () => import('./features/solution-catalog/solution-catalog.component')
          .then(m => m.SolutionCatalogComponent)
      },
      {
        path: 'solutions/:slug',
        loadComponent: () => import('./features/solution-detail/solution-detail.component')
          .then(m => m.SolutionDetailComponent)
      },
      {
        path: 'categories',
        loadChildren: () => import('./features/categories/categories.module')
          .then(m => m.CategoriesModule)
      },
      {
        path: 'departments',
        loadChildren: () => import('./features/departments/departments.module')
          .then(m => m.DepartmentsModule)
      },
      {
        path: 'about',
        loadChildren: () => import('./features/about/about.module')
          .then(m => m.AboutModule)
      }
    ]
  }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }