import { Component } from '@angular/core';

@Component({
  selector: 'tc-layout',
  templateUrl: './layout.component.html',
  styleUrls: ['./layout.component.scss']
})
export class LayoutComponent {
  menuItems = [
    { label: 'Solutions', icon: 'pi pi-compass', routerLink: '/solutions' },
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