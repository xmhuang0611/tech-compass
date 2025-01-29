import { NgModule } from '@angular/core';
import { RouterModule } from '@angular/router';
import { SharedModule } from '../../shared/shared.module';
import { DepartmentsComponent } from './departments.component';

@NgModule({
  declarations: [DepartmentsComponent],
  imports: [
    SharedModule,
    RouterModule.forChild([
      { path: '', component: DepartmentsComponent }
    ])
  ]
})
export class DepartmentsModule { } 