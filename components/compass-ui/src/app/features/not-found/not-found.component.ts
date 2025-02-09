import { Component, OnInit, OnDestroy } from "@angular/core";
import { CommonModule } from "@angular/common";
import { Router } from "@angular/router";
import { interval, Subscription } from "rxjs";
import { take } from "rxjs/operators";

@Component({
  selector: "app-not-found",
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="not-found">
      <div class="content">
        <h1>404</h1>
        <h2>Page Not Found</h2>
        <p>The page you are looking for does not exist.</p>
        <p class="countdown">
          Redirecting to homepage in {{ countdown }} seconds...
        </p>
      </div>
    </div>
  `,
  styles: [
    `
      .not-found {
        min-height: calc(
          100vh - 64px - 64px
        ); /* Subtract header and footer heights */
        display: flex;
        align-items: center;
        justify-content: center;
        background: var(--surface-ground);
        text-align: center;
        padding: 2rem;
        margin: 0;
      }

      .content {
        background: var(--surface-card);
        padding: 3rem;
        border-radius: var(--border-radius);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        max-width: 480px;
        width: 100%;
        margin: 2rem auto;
      }

      h1 {
        font-size: 6rem;
        font-weight: 700;
        color: var(--primary-color);
        margin: 0;
        line-height: 1;
      }

      h2 {
        font-size: 2rem;
        color: var(--text-color);
        margin: 1rem 0;
      }

      p {
        color: var(--text-color-secondary);
        margin: 1rem 0;
        font-size: 1.1rem;
      }

      .countdown {
        font-weight: 500;
        color: var(--primary-color);
      }

      @media screen and (max-height: 600px) {
        .not-found {
          min-height: auto;
          padding: 4rem 2rem;
        }
      }
    `,
  ],
})
export class NotFoundComponent implements OnInit, OnDestroy {
  countdown = 10;
  private countdownSubscription?: Subscription;

  constructor(private router: Router) {}

  ngOnInit() {
    this.startCountdown();
  }

  ngOnDestroy() {
    if (this.countdownSubscription) {
      this.countdownSubscription.unsubscribe();
    }
  }

  private startCountdown() {
    this.countdownSubscription = interval(1000)
      .pipe(take(10))
      .subscribe({
        next: (count) => {
          this.countdown = 10 - count - 1;
        },
        complete: () => {
          this.router.navigate(["/"]);
        },
      });
  }
}
