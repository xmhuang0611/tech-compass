import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { ButtonModule } from 'primeng/button';
import { CardModule } from 'primeng/card';
import { ChipModule } from 'primeng/chip';

@Component({
  selector: 'app-solution-card',
  standalone: true,
  imports: [CommonModule, RouterModule, ButtonModule, CardModule, ChipModule],
  templateUrl: './solution-card.component.html',
  styleUrls: ['./solution-card.component.scss']
})
export class SolutionCardComponent {
  @Input() solution: any; // TODO: Add proper interface
  @Input() showNewBadge: boolean = false;
} 