import { NgModule } from '@angular/core';
import { RouterModule } from '@angular/router';
import { SharedModule } from '../../shared/shared.module';
import { HomeComponent } from './home.component';
import { HttpClientModule } from '@angular/common/http';

import { CardModule } from 'primeng/card';
import { InputTextModule } from 'primeng/inputtext';
import { ButtonModule } from 'primeng/button';
import { ChipModule } from 'primeng/chip';
import { ProgressSpinnerModule } from 'primeng/progressspinner';
import { MessageModule } from 'primeng/message';
import { CarouselModule } from 'primeng/carousel';

@NgModule({
  declarations: [HomeComponent],
  imports: [
    SharedModule,
    HttpClientModule,
    CardModule,
    InputTextModule,
    ButtonModule,
    ChipModule,
    ProgressSpinnerModule,
    MessageModule,
    CarouselModule,
    RouterModule.forChild([
      { path: '', component: HomeComponent }
    ])
  ]
})
export class HomeModule { } 