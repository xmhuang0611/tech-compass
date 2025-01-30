import { Component } from '@angular/core';
import { siteConfig } from '../config/site.config';

@Component({
  selector: 'tc-layout',
  templateUrl: './layout.component.html',
  styleUrls: ['./layout.component.scss']
})
export class LayoutComponent {
  config = siteConfig;
  
  menuItems = [
    { label: 'Home', routerLink: '/' },
    { label: 'Solution Catalog', routerLink: '/solution-catalog' },
    { label: 'Categories', icon: 'pi pi-tags', routerLink: '/categories' },
    { label: 'Departments', icon: 'pi pi-users', routerLink: '/departments' },
    { label: 'About', icon: 'pi pi-info-circle', routerLink: '/about' }
  ];

  showSearch() {
    // TODO: Implement search functionality
    console.log('Search clicked');
  }

  showUserMenu() {
    // TODO: Implement user menu functionality
    console.log('User menu clicked');
  }
} 