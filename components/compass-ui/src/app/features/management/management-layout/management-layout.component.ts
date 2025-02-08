import { Component, OnInit, OnDestroy } from "@angular/core";
import { MenuItem } from "primeng/api";
import { ActivatedRoute, NavigationEnd, Router } from "@angular/router";
import { filter, Subscription } from "rxjs";

@Component({
  selector: "tc-management-layout",
  templateUrl: "./management-layout.component.html",
  styleUrls: ["./management-layout.component.scss"],
})
export class ManagementLayoutComponent implements OnInit, OnDestroy {
  breadcrumbItems: MenuItem[] = [];
  sideMenuItems: MenuItem[] = [];
  sidebarCollapsed = false;
  private routerSubscription: Subscription | undefined;

  constructor(private router: Router, private activatedRoute: ActivatedRoute) {}

  ngOnInit() {
    this.initializeSideMenu();
    this.setupBreadcrumbSubscription();
  }

  ngOnDestroy() {
    if (this.routerSubscription) {
      this.routerSubscription.unsubscribe();
    }
  }

  toggleSidebar() {
    this.sidebarCollapsed = !this.sidebarCollapsed;
  }

  private setupBreadcrumbSubscription() {
    this.routerSubscription = this.router.events
      .pipe(filter((event) => event instanceof NavigationEnd))
      .subscribe(() => {
        this.updateBreadcrumb();
      });

    // Initial breadcrumb setup
    this.updateBreadcrumb();
  }

  private updateBreadcrumb() {
    const breadcrumbs: MenuItem[] = [
      { label: "Home", routerLink: "/" },
      { label: "Manage Content", routerLink: "/manage" },
    ];

    let route = this.activatedRoute.firstChild;
    let url = "/manage";

    while (route) {
      if (route.snapshot.data["breadcrumb"]) {
        const path = route.snapshot.url
          .map((segment) => segment.path)
          .join("/");
        if (path) {
          url += `/${path}`;
        }
        // Only add the breadcrumb if it's not already the last item
        const label = route.snapshot.data["breadcrumb"];
        if (breadcrumbs[breadcrumbs.length - 1]?.label !== label) {
          breadcrumbs.push({
            label: label,
            routerLink: url,
          });
        }
      }
      route = route.firstChild;
    }

    this.breadcrumbItems = breadcrumbs;
  }

  private initializeSideMenu() {
    this.sideMenuItems = [
      {
        label: "Dashboard",
        icon: "pi pi-chart-bar",
        routerLink: "/manage",
        routerLinkActiveOptions: { exact: true },
      },
      {
        label: "My Solutions",
        icon: "pi pi-box",
        routerLink: "/manage/my-solutions",
      },
      {
        label: "My Comments",
        icon: "pi pi-comments",
        routerLink: "/manage/my-comments",
      },
      {
        label: "My Ratings",
        icon: "pi pi-star",
        routerLink: "/manage/my-ratings",
      },
    ];
  }
}
