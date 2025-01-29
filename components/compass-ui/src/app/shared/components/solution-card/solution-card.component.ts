import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { ButtonModule } from 'primeng/button';
import { CardModule } from 'primeng/card';
import { ChipModule } from 'primeng/chip';
import { TagModule } from 'primeng/tag';
import { Solution } from '../../interfaces/solution.interface';

type TagSeverity = 'success' | 'info' | 'warning' | 'danger';

@Component({
  selector: 'app-solution-card',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    ButtonModule,
    CardModule,
    ChipModule,
    TagModule
  ],
  templateUrl: './solution-card.component.html',
  styleUrls: ['./solution-card.component.scss']
})
export class SolutionCardComponent {
  @Input() solution!: Solution;
  @Input() showNewBadge: boolean = false;

  getRecommendStatusSeverity(): TagSeverity {
    switch (this.solution.recommend_status) {
      case 'BUY':
        return 'success';
      case 'HOLD':
        return 'warning';
      case 'SELL':
        return 'danger';
      default:
        return 'info';
    }
  }
} 