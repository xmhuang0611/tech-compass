import { NgModule } from '@angular/core';
import { RouterModule } from '@angular/router';
import { SharedModule } from '../../shared/shared.module';
import { SolutionsComponent } from './solutions.component';

@NgModule({
  declarations: [SolutionsComponent],
  imports: [
    SharedModule,
    RouterModule.forChild([
      { path: '', component: SolutionsComponent }
    ])
  ]
})
export class SolutionsModule { } 