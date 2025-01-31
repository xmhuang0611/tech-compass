import { Component, OnInit, ViewChild } from '@angular/core';
import { DialogService } from 'primeng/dynamicdialog';
import { MenuItem } from 'primeng/api';
import { Menu } from 'primeng/menu';
import { siteConfig } from '../config/site.config';
import { AuthService } from '../services/auth.service';
import { LoginDialogComponent } from '../components/login-dialog/login-dialog.component';

@Component({
  selector: 'tc-layout',
  templateUrl: './layout.component.html',
  styleUrls: ['./layout.component.scss'],
  providers: [DialogService]
})
export class LayoutComponent implements OnInit {
  @ViewChild('userMenu') userMenu!: Menu;
  
  config = siteConfig;
  menuItems: MenuItem[] = [];
  userMenuItems: MenuItem[] = [];
  
  constructor(
    private dialogService: DialogService,
    private authService: AuthService
  ) {}

  ngOnInit() {
    this.initializeMenus();
    this.authService.currentUser$.subscribe(user => {
      if (user) {
        this.userMenuItems = [
          {
            label: user.full_name,
            items: [
              {
                label: 'Logout',
                icon: 'pi pi-sign-out',
                command: () => this.logout()
              }
            ]
          }
        ];
      } else {
        this.userMenuItems = [];
      }
    });
  }

  private initializeMenus() {
    this.menuItems = this.config.navigation.map(item => ({
      label: item.label,
      icon: item.icon,
      routerLink: item.path
    }));
  }

  showSearch() {
    // TODO: Implement search functionality
  }

  onUserIconClick(event: Event) {
    if (!this.authService.isLoggedIn()) {
      this.showLoginDialog();
    } else if (this.userMenu) {
      this.userMenu.toggle(event);
    }
  }

  showLoginDialog() {
    const ref = this.dialogService.open(LoginDialogComponent, {
      width: '400px',
      header: ' ',
      contentStyle: { padding: 0 },
      baseZIndex: 1000,
      style: {
        'box-shadow': '0 4px 20px rgba(0, 0, 0, 0.1)'
      }
    });

    ref.onClose.subscribe((success: boolean) => {
      // Handle successful login if needed
    });
  }

  logout() {
    this.authService.logout();
  }
} 