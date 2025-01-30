import { Component } from '@angular/core';
import { siteConfig } from '../config/site.config';

@Component({
  selector: 'tc-layout',
  templateUrl: './layout.component.html',
  styleUrls: ['./layout.component.scss']
})
export class LayoutComponent {
  config = siteConfig;
  
  menuItems = this.config.navigation.map(item => ({
    label: item.label,
    icon: item.icon,
    routerLink: item.path
  }));

  showSearch() {
    // TODO: Implement search functionality
    console.log('Search clicked');
  }

  showUserMenu() {
    // TODO: Implement user menu functionality
    console.log('User menu clicked');
  }
} 