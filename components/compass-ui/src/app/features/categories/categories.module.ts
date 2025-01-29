import { NgModule } from '@angular/core';
import { RouterModule } from '@angular/router';
import { SharedModule } from '../../shared/shared.module';
import { CategoriesComponent } from './categories.component';

@NgModule({
  declarations: [CategoriesComponent],
  imports: [
    SharedModule,
    RouterModule.forChild([
      { path: '', component: CategoriesComponent }
    ])
  ]
})
export class CategoriesModule { } 