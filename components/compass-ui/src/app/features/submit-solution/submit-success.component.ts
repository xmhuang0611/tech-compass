import { Component } from '@angular/core';

@Component({
  selector: 'app-submit-success',
  template: `
    <div class="submit-success">
      <div class="success-content">
        <div class="icon-container">
          <i class="pi pi-check-circle"></i>
        </div>
        <h1>Thank You!</h1>
        <p class="message">
          Your solution has been submitted successfully and is pending review.
          We will carefully evaluate your submission and make it visible
          once approved. Please be patient during this process.
        </p>
        <div class="actions">
          <button pButton type="button" label="Submit Another Solution" 
            icon="pi pi-plus" routerLink="/solutions/new">
          </button>
          <button pButton type="button" label="Back to Home" 
            icon="pi pi-home" routerLink="/" 
            class="p-button-outlined">
          </button>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .submit-success {
      max-width: 800px;
      margin: 4rem auto;
      padding: 2rem;
      text-align: center;
    }

    .success-content {
      background: var(--surface-card);
      border-radius: var(--border-radius);
      padding: 3rem;
      box-shadow: var(--card-shadow);
    }

    .icon-container {
      margin-bottom: 1.5rem;

      .pi-check-circle {
        font-size: 4rem;
        color: var(--green-500);
      }
    }

    h1 {
      color: var(--text-color);
      margin: 0 0 1rem 0;
    }

    .message {
      color: var(--text-color-secondary);
      font-size: 1.1rem;
      line-height: 1.5;
      margin-bottom: 2rem;
    }

    .actions {
      display: flex;
      gap: 1rem;
      justify-content: center;

      button {
        min-width: 200px;
      }
    }
  `]
})
export class SubmitSuccessComponent { }
