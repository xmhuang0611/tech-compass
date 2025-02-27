import { Component } from "@angular/core";
import { CommonModule } from "@angular/common";
import { FormsModule } from "@angular/forms";
import { DynamicDialogRef } from "primeng/dynamicdialog";
import { ButtonModule } from "primeng/button";
import { InputTextModule } from "primeng/inputtext";
import { PasswordModule } from "primeng/password";
import { MessageModule } from "primeng/message";
import { RippleModule } from "primeng/ripple";
import { AuthService } from "../../services/auth.service";
import { siteConfig } from "../../config/site.config";

@Component({
  selector: "app-login-dialog",
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    ButtonModule,
    InputTextModule,
    PasswordModule,
    MessageModule,
    RippleModule,
  ],
  template: `
    <div class="sign-in-dialog" (keydown.enter)="onSignIn()">
      <div class="dialog-header">
        <h2>{{ config.auth.signIn.title }}</h2>
        <p class="subtitle">{{ config.auth.signIn.subtitle }}</p>
      </div>

      <div class="dialog-content">
        <div class="field">
          <label for="username">{{ config.auth.signIn.usernameLabel }}</label>
          <span class="p-input-icon-left">
            <i class="pi pi-user"></i>
            <input
              id="username"
              type="text"
              pInputText
              [(ngModel)]="username"
              [class.ng-invalid]="submitted && !username"
              [placeholder]="config.auth.signIn.usernamePlaceholder"
            />
          </span>
        </div>

        <div class="field">
          <label for="password">{{ config.auth.signIn.passwordLabel }}</label>
          <div class="password-wrapper">
            <i class="pi pi-lock"></i>
            <p-password
              id="password"
              [(ngModel)]="password"
              [feedback]="false"
              [toggleMask]="true"
              [class.ng-invalid]="submitted && !password"
              [placeholder]="config.auth.signIn.passwordPlaceholder"
              [style]="{ width: '100%' }"
            ></p-password>
          </div>
        </div>

        <p-message
          *ngIf="errorMessage"
          severity="error"
          [text]="errorMessage"
          styleClass="w-full"
        ></p-message>
      </div>

      <div class="dialog-footer">
        <p-button
          [label]="config.auth.signIn.cancelButton"
          (click)="onCancel()"
          styleClass="p-button-text p-button-secondary"
        ></p-button>
        <p-button
          [label]="config.auth.signIn.signInButton"
          (click)="onSignIn()"
          [loading]="loading"
          icon="pi pi-sign-in"
          styleClass="p-button-primary"
          pRipple
        ></p-button>
      </div>
    </div>
  `,
  styles: [
    `
      .sign-in-dialog {
        padding: 1.5rem;
        min-width: 350px;
      }

      .dialog-header {
        text-align: center;
        margin-bottom: 2rem;

        h2 {
          margin: 0;
          font-size: 1.75rem;
          font-weight: 600;
          color: var(--text-color);
        }

        .subtitle {
          margin: 0.5rem 0 0 0;
          color: var(--text-color-secondary);
        }
      }

      .dialog-content {
        margin-bottom: 2rem;
      }

      .field {
        margin-bottom: 1.5rem;

        label {
          display: block;
          margin-bottom: 0.5rem;
          color: var(--text-color-secondary);
          font-size: 0.875rem;
        }

        .p-input-icon-left {
          width: 100%;

          i {
            color: var(--text-color-secondary);
          }
        }

        input {
          width: 100%;
          padding-left: 2.5rem;
        }
      }

      .dialog-footer {
        display: flex;
        justify-content: flex-end;
        gap: 0.5rem;
      }

      .password-wrapper {
        position: relative;
        width: 100%;

        i.pi-lock {
          position: absolute;
          left: 0.75rem;
          top: 50%;
          transform: translateY(-50%);
          z-index: 1;
          color: var(--text-color-secondary);
        }
      }

      :host ::ng-deep {
        .p-password {
          width: 100%;

          input {
            width: 100%;
            padding-left: 2.5rem;
          }
        }

        .p-message {
          margin-bottom: 1rem;
        }

        .p-button {
          .p-button-label {
            font-weight: 600;
          }

          &.p-button-primary {
            background: var(--primary-color);
            border-color: var(--primary-color);
            color: var(--primary-color-text);

            &:enabled:hover {
              background: var(--primary-600);
              border-color: var(--primary-600);
            }
          }

          &.p-button-secondary {
            color: var(--text-color-secondary);

            &:enabled:hover {
              background: rgba(0, 0, 0, 0.04);
              color: var(--text-color);
            }
          }
        }
      }
    `,
  ],
})
export class LoginDialogComponent {
  config = siteConfig;
  username = "";
  password = "";
  loading = false;
  errorMessage = "";
  submitted = false;

  constructor(
    private authService: AuthService,
    private ref: DynamicDialogRef
  ) {}

  onSignIn(): void {
    this.submitted = true;

    if (!this.username || !this.password) {
      this.errorMessage = this.config.auth.signIn.errors.emptyFields;
      return;
    }

    this.loading = true;
    this.errorMessage = "";

    this.authService.login(this.username, this.password).subscribe({
      next: () => {
        this.ref.close(true);
      },
      error: (error) => {
        this.loading = false;
        // Check for specific inactive user error message
        if (error.error?.detail && error.error.detail.includes("inactive")) {
          this.errorMessage = this.config.auth.signIn.errors.inactiveUser;
        } else {
          this.errorMessage =
            error.error?.detail || this.config.auth.signIn.errors.defaultError;
        }
      },
    });
  }

  onCancel(): void {
    this.ref.close(false);
  }
}
