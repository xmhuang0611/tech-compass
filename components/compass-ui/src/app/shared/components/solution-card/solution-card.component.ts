import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { ButtonModule } from 'primeng/button';
import { CardModule } from 'primeng/card';
import { ChipModule } from 'primeng/chip';
import { TagModule } from 'primeng/tag';
import { RatingModule } from 'primeng/rating';
import { Solution } from '../../interfaces/solution.interface';

type TagSeverity = 'success' | 'info' | 'warning' | 'danger';

@Component({
  selector: 'app-solution-card',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    RouterModule,
    ButtonModule,
    CardModule,
    ChipModule,
    TagModule,
    RatingModule
  ],
  templateUrl: './solution-card.component.html',
  styleUrls: ['./solution-card.component.scss']
})
export class SolutionCardComponent {
  @Input() solution!: Solution;
  @Input() showNewBadge: boolean = false;

  getRecommendStatusSeverity(): TagSeverity {
    switch (this.solution.recommend_status) {
      case 'ADOPT':
        return 'success';
      case 'TRIAL':
        return 'info';
      case 'ASSESS':
        return 'warning';
      case 'HOLD':
        return 'danger';
      default:
        return 'info';
    }
  }

  /**
   * Rounds a number to the nearest 0.5
   * @param value The number to round
   * @returns The rounded number
   */
  roundToHalf(value: number): number {
    return Math.round(value * 2) / 2;
  }
} 