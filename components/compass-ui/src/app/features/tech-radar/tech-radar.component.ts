import { Component } from '@angular/core';

@Component({
  selector: 'tc-tech-radar',
  standalone: true,
  template: `
    <div class="tech-radar-container">
      <div class="coming-soon-content">
        <img src="assets/tech-radar.svg" alt="Tech Radar" class="radar-icon" />
        <h1>Tech Radar Coming Soon</h1>
        <p>We're working on something exciting! Our Tech Radar feature will help you navigate the technology landscape.</p>
        <p>Please stay tuned for updates.</p>
      </div>
    </div>
  `,
  styles: [`
    .tech-radar-container {
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: calc(100vh - 200px);
      padding: 2rem;
    }

    .coming-soon-content {
      text-align: center;
      max-width: 600px;
      padding: 3rem;
      background: var(--surface-card);
      border-radius: var(--border-radius);
      box-shadow: var(--card-shadow);
    }

    .radar-icon {
      width: 120px;
      height: 120px;
      margin-bottom: 2rem;
      color: var(--primary-color);
    }

    h1 {
      color: var(--primary-color);
      font-size: 2.5rem;
      margin-bottom: 1.5rem;
      font-weight: 600;
    }

    p {
      color: var(--text-color-secondary);
      font-size: 1.1rem;
      line-height: 1.6;
      margin-bottom: 1rem;

      &:last-child {
        margin-bottom: 0;
      }
    }
  `]
})
export class TechRadarComponent {}