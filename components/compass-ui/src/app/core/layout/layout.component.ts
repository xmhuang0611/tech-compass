import { Component, OnInit, ViewChild } from '@angular/core';
import { DialogService } from 'primeng/dynamicdialog';
import { MenuItem } from 'primeng/api';
import { Menu } from 'primeng/menu';
import { siteConfig } from '../config/site.config';
import { NavigationItem, SubMenuNavigationItem, InternalNavigationItem, ExternalNavigationItem } from '../types/navigation.types';
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
    this.menuItems = this.config.navigation.map(item => {
      const menuItem: MenuItem = {
        label: item.label,
        icon: item.icon
      };

      if (this.isInternalLink(item)) {
        menuItem.routerLink = item.path;
      }
      else if (this.isExternalLink(item)) {
        menuItem.url = item.url;
        menuItem.target = item.target;
      }
      else if (this.isSubMenu(item)) {
        menuItem.items = item.items.map((subItem: InternalNavigationItem | ExternalNavigationItem) => {
          const subMenuItem: MenuItem = {
            label: subItem.label,
            icon: subItem.icon
          };
          
          if ('url' in subItem) {
            subMenuItem.url = subItem.url;
            subMenuItem.target = subItem.target;
          } else if ('path' in subItem) {
            subMenuItem.routerLink = subItem.path;
          }
          
          return subMenuItem;
        });
      }

      return menuItem;
    });
  }

  private isSubMenu(item: NavigationItem): item is SubMenuNavigationItem {
    return 'items' in item && Array.isArray(item.items);
  }

  private isInternalLink(item: NavigationItem): item is InternalNavigationItem {
    return 'path' in item;
  }

  private isExternalLink(item: NavigationItem): item is ExternalNavigationItem {
    return 'url' in item;
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